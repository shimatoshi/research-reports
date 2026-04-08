# APK内蔵Python完全ガイド (2026-04-09)

## 概要
Android APKにCPython 3.13 + Flask + クローラーを内蔵し、
アプリ内でWebサーバーを起動する自己完結型アプリの構築知見。
Chaquopy/p4aに依存しない方式。

## アーキテクチャ

```
APK
├── lib/arm64-v8a/
│   ├── libpython_launcher.so   ← JNIエントリポイント（Cで実装）
│   ├── libpython3.13.so        ← CPython本体
│   ├── libandroid-support.so
│   ├── libcrypto3.so / libssl3.so
│   └── libcurl_cffi_wrapper.so ← TLSフィンガープリント対策
├── assets/
│   ├── python-bundle.bin       ← Python stdlib + site-packages (tar.gz)
│   └── app-source/             ← アプリのPythonソース + frontend
└── classes*.dex                ← Java (MainActivity + PythonLauncher)
```

### 起動フロー
1. `MainActivity.extractPythonBundle()` — assets/python-bundle.binをfiles/に展開
2. `MainActivity.extractAppSource()` — assets/app-source/をfiles/にコピー
3. `PythonLauncher.setEnv()` — Cレベルで環境変数を設定
4. `PythonLauncher.runPython(["python3", "boot.py"])` — JNI経由でPy_Main呼び出し
5. `boot.py` — Flask app.run() でサーバー起動
6. `MainActivity.waitForServer()` — /api/versionをポーリング
7. WebViewで`http://127.0.0.1:8789`を表示

## 致命的な落とし穴と解決策

### 1. ProcessBuilder方式は使えない（SELinux）

**症状**: `error=13, Permission denied` でpython3バイナリが実行できない

```
avc: denied { execute_no_trans } for path=".../python3"
```

**原因**: Android 7+のSELinuxポリシーがアプリのdata領域にある実行ファイルの
fork+execを禁止している。ProcessBuilderはfork+execなので弾かれる。

**解決**: JNI経由でPy_Main()を直接呼ぶ。同一プロセス内でPythonが動くため
execが不要。

```java
// NG: ProcessBuilder方式
ProcessBuilder pb = new ProcessBuilder(python.getAbsolutePath(), server.getAbsolutePath());
pb.start(); // → SELinux denied

// OK: JNI方式
PythonLauncher.runPython(new String[]{"python3", "boot.py"});
```

### 2. LD_LIBRARY_PATHが効かない（Android Linker Namespace）

**症状**: `dlopen failed: library "libz.so.1" not found`

**原因**: Android 7+ではLinker Namespaceの制限により、
アプリのコードから`LD_LIBRARY_PATH`を設定しても
動的リンカがそれを無視する。APKの`lib/`ディレクトリだけが検索対象。

**解決**: `libpython_launcher.so`のCコード内で、Py_Main呼び出し前に
`dlopen(RTLD_NOW | RTLD_GLOBAL)`で手動プリロードする。

```c
// python_launcher.c — runPython()内
const char *libs[] = {
    "libz.so.1", "libffi.so", "libsqlite3.so", "libexpat.so.1",
    "liblzma.so.5", "libbz2.so.1.0", "libcrypto3.so", "libssl3.so",
    "libandroid-support.so", NULL
};
char *ld_path = getenv("LD_LIBRARY_PATH");
// LD_LIBRARY_PATHの最初のエントリからフルパスを構築してdlopen
for (int i = 0; libs[i]; i++) {
    char fullpath[1024];
    snprintf(fullpath, sizeof(fullpath), "%s/%s", ld_path, libs[i]);
    dlopen(fullpath, RTLD_NOW | RTLD_GLOBAL);
}
```

**重要**: `LD_LIBRARY_PATH`の設定時、python-bundleのlibパスを**先頭**に置くこと。

```java
// bundleのlibを先に（Cコードがプリロードに使う）
String bundleLibDir = new File(pythonDir, "lib").getAbsolutePath();
PythonLauncher.setEnv("LD_LIBRARY_PATH", bundleLibDir + ":" + nativeLibDir);
```

### 3. 環境変数がネイティブコードに伝わらない

**症状**: PythonがPYTHONHOMEやPYTHONPATHを認識しない

**原因**: JavaのProcessBuilder.environment()やSystem.getenv()の変更は
JVMレベルの話であり、Cライブラリの`getenv()`には反映されない。

**解決**: JNI経由でCの`setenv()`を直接呼ぶ。

```c
JNIEXPORT void JNICALL
Java_net_localnet_app_PythonLauncher_setEnv(JNIEnv *env, jclass cls,
                                             jstring key, jstring value) {
    const char *k = (*env)->GetStringUTFChars(env, key, NULL);
    const char *v = (*env)->GetStringUTFChars(env, value, NULL);
    setenv(k, v, 1);
    (*env)->ReleaseStringUTFChars(env, key, k);
    (*env)->ReleaseStringUTFChars(env, value, v);
}
```

### 4. PYTHONHOMEのディレクトリ構造

**症状**: `ModuleNotFoundError: No module named 'encodings'`

**原因**: CPython 3.13は`PYTHONHOME/lib/python3.13/`にstdlibを期待するが、
python-bundle内では`stdlib/`に直接配置している。

**解決**: シンボリックリンクを作成する。

```java
File symlinkTarget = new File(pythonDir, "lib/python3.13");
symlinkTarget.getParentFile().mkdirs();
Files.createSymbolicLink(symlinkTarget.toPath(),
        new File(pythonDir, "stdlib").toPath());
```

### 5. python-bundle.tar.gzがAPKに含まれない

**症状**: `FileNotFoundException: python-bundle.tar.gz` (assets.open時)

**原因**: Gradleのassetパッケージングが`.tar.gz`ファイルを
内部的にgzip展開して`.tar`にリネームしてしまう。
`aaptOptions { noCompress "tar.gz" }` を設定しても効かないケースがある。

**解決**: 拡張子を`.bin`に変更する。Gradleは`.bin`を触らない。

```
assets/python-bundle.bin   ← 実体はtar.gz、拡張子だけ変えてある
```

```java
try (InputStream is = getAssets().open("python-bundle.bin");
     GZIPInputStream gis = new GZIPInputStream(is)) {
    extractTar(gis, getFilesDir());
}
```

### 6. python-bundle.binの中身の違いに注意

python-bundleには2種類のビルドが存在しうる:

| サイズ | 内容 |
|--------|------|
| ~11MB | stdlib + site-packages のみ（共有ライブラリなし） |
| ~21MB | stdlib + site-packages + lib/*.so（libz, libffi等含む） |

**21MBの方が正解**。共有ライブラリが含まれていないと
`dlopen failed: library "libz.so.1" not found` が発生する。

python-bundle/lib/ に含まれるべきファイル:
```
libandroid-support.so
libbz2.so.1.0
libcrypto3.so
libexpat.so.1
libffi.so
liblzma.so.5
libsqlite3.so
libssl3.so
libz.so.1
```

### 7. Termux環境でのビルド制約

**症状**: `stripDebugDebugSymbols` タスクが失敗

**原因**: NDKのllvm-stripはx86_64バイナリであり、
Termux(aarch64)上では実行できない。

**解決**: build.gradleにdoNotStripを追加。

```gradle
packagingOptions {
    doNotStrip '**/*.so'
}
```

### 8. 開発版と安定版の共存

**絶対ルール**: 安定版APKをアンインストールしない。

開発版は別applicationIdでインストールし、安定版と共存させる。

```gradle
// build.gradle
defaultConfig {
    applicationId "net.localnet.app.dev"  // 安定版: net.localnet.app
}
```

起動時のActivity指定はnamespace（package名）を使う:
```bash
# applicationIdとnamespaceが異なる場合
adb shell am start -n net.localnet.app.dev/net.localnet.app.MainActivity
```

ポートが衝突する場合は安定版を`am force-stop`してからテスト。

## 必要な環境変数

| 変数 | 値 | 設定方法 |
|------|----|----|
| LD_LIBRARY_PATH | `{bundleLib}:{nativeLib}` | PythonLauncher.setEnv() |
| PYTHONHOME | python-bundleディレクトリ | PythonLauncher.setEnv() |
| PYTHONPATH | `{stdlib}:{site-packages}:{appDir}` | PythonLauncher.setEnv() |
| LOCALNET_BASE | アプリのfilesディレクトリ | PythonLauncher.setEnv() |
| LOCALNET_PORT | 8789 | PythonLauncher.setEnv() |

## ネイティブライブラリのコンパイル

Termux上でネイティブビルド（ARM64→ARM64、クロスコンパイル不要）:

```bash
clang -shared -fPIC -o libpython_launcher.so python_launcher.c \
    -I/usr/include/python3.13 -lpython3.13 \
    -target aarch64-linux-android26
```

## 文字コード関連の知見

### クローラーのEUC-JP/Shift_JIS対応

HTMLのcharset検出後にUTF-8へデコードするが、以下の2点を忘れると文字化けする:

1. **meta charset宣言の書き換え**: HTMLをUTF-8で保存する以上、
   `<meta charset="EUC-JP">` を `<meta charset="utf-8">` に変更必須。
   放置するとカタログ生成時にEUC-JPとして再デコードされ二重に化ける。

2. **CSSファイルの文字コード検出**: 外部CSSもEUC-JP等で書かれている場合がある。
   `@charset` 宣言を検出し、HTMLページのcharsetをフォールバックに使う。
   保存時はUTF-8に統一し、`@charset "utf-8"` に書き換える。
