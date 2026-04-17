# browser-save

Chromiumを1回だけ起動し、ページをシングルファイルHTMLとして保存する。

ブラウザが普通にページを読み込む → DOM+キャッシュ済みリソースからインライン化 → 追加リクエストなし。
サーバーから見たら普通のブラウジングと同じアクセスパターン。

## 使い方

### ワンショット（1ページ保存）

```bash
node index.js "https://example.com/page" output.html
```

### サーバーモード（ブラウザ起動しっぱなし、HTTP経由で依頼）

```bash
node index.js --server 3100
```

```bash
# ページ保存
curl -X POST http://localhost:3100/save \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com/page", "output": "/path/to/output.html"}'

# 終了
curl -X POST http://localhost:3100/quit \
  -H 'Content-Type: application/json' -d '{}'
```

### Pythonクローラーから使う

`browser_crawler.py` がサーバーモードを自動起動してBFSクロールする。
localnetプロジェクトの `jobs.py` に統合済み。

```python
from browser_crawler import BrowserCrawler

crawler = BrowserCrawler("https://example.com", delay=2.0)
crawler.run()
```

## CPU負荷

- Chromium起動は1回だけ。ページごとにタブを開閉するだけなので軽い
- インライン化はブラウザ内JSで実行。画像はcanvasから（デコード済み）、CSSはCSSOMから読むだけ
- `stop()` でブラウザプロセスごと即kill

## proot-distro環境（Android/Termux）

```bash
# セットアップ（1回だけ）
proot-distro login ubuntu
apt update && apt install -y chromium nodejs npm
npm install -g puppeteer

# Termuxから呼ぶ
proot-distro login ubuntu -- node /path/to/index.js --server 3100
```

## 構成

| ファイル | 内容 |
|----------|------|
| `index.js` | Node.js — Puppeteer永続ブラウザ + HTTPサーバー + DOMインライン化 |
| `browser_crawler.py` | Python — サーバーモードを使ったBFSクローラー |
| `package.json` | 依存: puppeteer |
