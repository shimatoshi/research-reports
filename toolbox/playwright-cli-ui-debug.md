# Playwright: CLIからUIを操作・デバッグする

Claude Code等のCLIツールから、ブラウザUIをプログラム的に操作する方法。

## 方式

### 1. Playwright MCP（Claude Code向け）

```bash
claude mcp add playwright npx @playwright/mcp@latest
```

Claude Codeに `browser_navigate`, `browser_click`, `browser_snapshot` 等のツールが追加される。会話の中で「ブラウザでlocalhost:5173を開いて」と言えば操作できる。

- トークン消費: ~114kトークン/セッション（重い）
- アクセシビリティツリーで要素を認識

### 2. Playwright CLI（トークン効率重視）

```bash
npm install -g @playwright/cli
playwright-cli install
```

Bashから直接呼ぶ：
```bash
playwright-cli open http://localhost:5173 --headed
playwright-cli snapshot                    # ページ状態をYAMLで取得
playwright-cli click e15                   # 要素をクリック
playwright-cli fill e8 "検索ワード"         # 入力
playwright-cli screenshot                  # スクリーンショット保存
```

- トークン消費: ~27kトークン/セッション（MCPの1/4）
- スナップショットはファイルに保存→必要な時だけ読む

## 使い分け

- **MCP**: セットアップが楽。Claude Codeとの統合が自然
- **CLI**: トークン効率が良い。シェルアクセスがあるなら推奨

## Termux (Android) での動かし方

Playwright CLIはAndroid非対応だが、以下で動作する：

### 1. ラッパースクリプト作成
```bash
cat > /data/data/com.termux/files/usr/bin/playwright-cli << 'SCRIPT'
#!/usr/bin/env node
Object.defineProperty(process, 'platform', { value: 'linux' });
process.env.NODE_OPTIONS = (process.env.NODE_OPTIONS || '') +
  ' --require /data/data/com.termux/files/usr/lib/node_modules/@playwright/cli/termux-platform-patch.js';
const { program } = require('@playwright/cli/node_modules/playwright-core/lib/tools/cli-client/program');
const packageJson = require('@playwright/cli/package.json');
program({ embedderVersion: packageJson.version });
SCRIPT
chmod +x /data/data/com.termux/files/usr/bin/playwright-cli
```

プリロードパッチ（daemon子プロセス用）:
```bash
cat > /data/data/com.termux/files/usr/lib/node_modules/@playwright/cli/termux-platform-patch.js << 'PATCH'
if (process.platform === 'android') {
  Object.defineProperty(process, 'platform', { value: 'linux' });
}
PATCH
```

### 2. adb自己接続 + DevTools転送
```bash
# 端末の開発者オプションでワイヤレスデバッグを有効化 (port 5555)
adb connect localhost:5555
adb forward tcp:9222 localabstract:chrome_devtools_remote
```

### 3. 接続
```bash
playwright-cli attach --cdp ws://localhost:9222/devtools/browser
playwright-cli goto http://localhost:5173
playwright-cli snapshot
playwright-cli click e15
```

Brave/Chrome等のChromiumブラウザに接続して操作可能。

## 用途

- UI変更後の動作確認を自動化
- デバッグ: 画面遷移・ボタン押下・フォーム入力を再現
- Vite dev serverと組み合わせてAPKビルドなしにUI開発
