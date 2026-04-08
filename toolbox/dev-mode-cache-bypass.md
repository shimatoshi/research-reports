# 開発モード: Service Worker・キャッシュ無効化パターン

WebView + Flask（またはローカルサーバー）構成のアプリで、開発中にキャッシュが更新を妨げる問題の汎用解決策。

## 問題

- Service Workerがレスポンスをキャッシュし、コード変更が反映されない
- ブラウザ/WebViewのHTTPキャッシュも古いリソースを返す
- 毎回手動でキャッシュクリアするのは非現実的

## 解決: サーバー側で制御する開発モード

環境変数1つで開発モードをON/OFFする。フロントエンドはサーバーに問い合わせてモードを判定する。

### サーバー側（Python/Flask例）

```python
# config.py
DEV_MODE = os.environ.get('LOCALNET_DEV', '').lower() in ('1', 'true', 'yes')

# server.py
@app.after_request
def add_headers(response):
    if DEV_MODE:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# sw.jsのエンドポイント
@app.route('/sw.js')
def serve_sw():
    if DEV_MODE:
        # 空のSWで既存SWを上書き→fetchハンドラが消える
        return app.response_class('/* dev mode: no-op */', mimetype='application/javascript')
    return send_from_directory(FRONTEND_DIR, 'sw.js')

# バージョンAPIにフラグを含める
@app.route('/api/version')
def api_version():
    return jsonify({"version": VERSION, "dev_mode": DEV_MODE})
```

### フロントエンド側

```typescript
fetch('/api/version').then(r => r.json()).then(data => {
  if (data.dev_mode) {
    // SW全解除
    navigator.serviceWorker?.getRegistrations().then(regs =>
      regs.forEach(r => r.unregister())
    )
    // キャッシュ全削除
    caches?.keys().then(keys => keys.forEach(k => caches.delete(k)))
  } else {
    // 本番: SW登録
    navigator.serviceWorker?.register('/sw.js').catch(() => {})
  }
})
```

### 使い方

```bash
# 開発時
LOCALNET_DEV=1 python server.py

# 本番
python server.py
```

## ポイント

- **サーバーが真実の源**: フロントエンドは自分でモードを判定しない。サーバーのAPIレスポンスに従う
- **空のSWで上書き**: sw.jsを404にするのではなく、空のスクリプトを返す。これで既存の登録済みSWが上書きされ、fetchハンドラが消える
- **全レスポンスにno-cache**: `after_request` フックで一括付与。個別エンドポイントでの対応は不要
- **環境変数で制御**: コードの変更なしにモード切替可能。CI/本番では変数を設定しなければ自動的に本番モード

## 適用先

- WebView + ローカルサーバー構成のAndroidアプリ
- PWA開発
- Service Workerを使う任意のWebアプリ
