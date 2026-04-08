# APK内蔵クローラー 403問題の解決 (2026-04-08)

## 概要
APK内にPython + Flask + クローラーを内蔵する自己完結型アプリで、
多くのサイト(tapology, ポケ徹等)から403 Forbiddenが返される問題を解決した。

## 403の原因: TLSフィンガープリント

CloudflareなどのWAF(Web Application Firewall)は、TLSハンドシェイク時の
フィンガープリント(JA3/JA4)でbotを検知する。

- Python `requests` (urllib3) のTLSフィンガープリントはブラウザと全く異なる
- User-Agentを偽装しても、TLSフィンガープリントとの矛盾でむしろ怪しまれる
- `curl`コマンドも同様に弾かれる
- HTTP/2非対応も検知材料の一つ

### 検証結果
```
requests          → 403 (tapology, ポケ徹)
curl + 全ヘッダー → 403
curl_cffi(chrome) → 200 ← これが解決策
```

## 解決策: curl_cffi

`curl_cffi`はChromeのTLSフィンガープリントを完全に模倣するPythonライブラリ。
内部にlibcurl + BoringSSLを静的リンクしており、外部SSL依存がない。

```python
# Before (403が出る)
import requests
session = requests.Session()

# After (200が返る)
from curl_cffi import requests as cffi_requests
session = cffi_requests.Session(impersonate="chrome")
```

### Android対応
- `curl_cffi-0.15.0-cp313-abi3-android_24_arm64_v8a.whl` が公式提供されている
- pip installするだけでTermux上でも動作確認済み

## APKでPythonを動かすための知見

Chaquopy/p4aを使わず、素のCPython 3.13をAPKに内蔵する方式で以下の問題を解決した。

### 1. 環境変数がネイティブに伝わらない
JavaのリフレクションでSystem.getenv()のMapを変更しても、
CライブラリのgetenvO()には反映されない。

**解決**: JNI経由でCの`setenv()`を直接呼ぶ関数を追加。

```c
JNIEXPORT void JNICALL
Java_net_localnet_app_PythonLauncher_setEnv(JNIEnv *env, jclass cls, jstring key, jstring value) {
    const char *k = (*env)->GetStringUTFChars(env, key, NULL);
    const char *v = (*env)->GetStringUTFChars(env, value, NULL);
    setenv(k, v, 1);
    ...
}
```

### 2. PYTHONHOME のディレクトリ構造
CPython 3.13は `PYTHONHOME/lib/python3.13/` にstdlibを期待する。
`stdlib/`に直接ファイルを入れている場合、シンボリックリンクが必要。

```java
Files.createSymbolicLink(
    new File(pythonDir, "lib/python3.13").toPath(),
    new File(pythonDir, "stdlib").toPath()
);
```

### 3. Android Linker Namespaceの制限
Android 7+ではLD_LIBRARY_PATHが無効。バージョン付き.so（libz.so.1等）は
APKの`lib/`ディレクトリからしか検索されない。

**解決**: Py_Main呼び出し前に`dlopen(RTLD_NOW | RTLD_GLOBAL)`で手動プリロード。

```c
const char *libs[] = {
    "libz.so.1", "libffi.so", "libsqlite3.so", "libexpat.so.1",
    "liblzma.so.5", "libbz2.so.1.0", "libcrypto3.so", "libssl3.so",
    "libandroid-support.so", NULL
};
for (int i = 0; libs[i]; i++) {
    char fullpath[1024];
    snprintf(fullpath, sizeof(fullpath), "%s/%s", libdir, libs[i]);
    dlopen(fullpath, RTLD_NOW | RTLD_GLOBAL);
}
```

### 4. パッケージメタデータ(dist-info)
pipでインストールされたパッケージのdist-infoディレクトリも
site-packagesにコピーしないと、importlib.metadataで
PackageNotFoundErrorが発生する。

### 5. ビルド環境
- Termux上でネイティブビルド（ARM64→ARM64なのでクロスコンパイル不要）
- x86_64 NDKのツールチェインはTermux上で実行できない
- Termuxの`clang`で直接コンパイルすればOK

```bash
clang -shared -fPIC -o libpython_launcher.so python_launcher.c \
    -I/usr/include/python3.13 -lpython3.13 \
    -target aarch64-linux-android26
```

## 結論
- 403の99%はTLSフィンガープリント → curl_cffiで解決
- APK内Pythonは環境変数・ライブラリパス・ディレクトリ構造の3つを正しく設定すれば動く
- Chaquopyに頼らずとも、素のCPythonをAPKに内蔵可能
