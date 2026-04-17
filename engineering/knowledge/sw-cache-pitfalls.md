# Service Worker & ブラウザキャッシュの罠

## 背景

オフラインファースト開発（オンライン時にデータ収集 → オフラインで使う）をやると、SWのキャッシュが強すぎて変更が反映されない問題に毎回ハマる。プライベートブラウザ、キャッシュクリア、PWAアンインストールしても変わらない → 実はキャッシュじゃなかった、というパターンも含めて何度も繰り返してきた。

## 核心: キャッシュは2層ある

| 層 | SW無効でも効く？ | 制御方法 |
|---|---|---|
| HTTPキャッシュ（ブラウザ標準） | **はい** | `Cache-Control`ヘッダ |
| SW Cache API | いいえ | SW内のコードで制御 |

**SWを無効にしてもHTTPキャッシュは残る。** 「SWのせいかも」と思ってSWを消しても、HTTPキャッシュが効いていれば変わらないように見える。逆もまた然り。

## 開発環境: キャッシュさせない

### サーバー側で `Cache-Control: no-store`（推奨）

ブラウザや端末を問わず効く。一度設定すれば忘れても大丈夫。

```python
# FastAPI
@app.middleware("http")
async def no_cache_in_dev(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response
```

```js
// Vite (vite.config.ts)
export default defineConfig({
  server: {
    headers: { "Cache-Control": "no-store" }
  }
})
```

### SW登録を開発中は無効にする

```js
if (import.meta.env.PROD) {
  navigator.serviceWorker.register('/sw.js');
}
```

### DevTools（補助）

- Network > **Disable cache** （DevTools開いてる間だけ有効）
- Application > Service Workers > **Update on reload**

## 本番環境: 更新を確実に反映させる

### SW側

```js
self.addEventListener('install', (e) => {
  self.skipWaiting(); // 待機せず即アクティブ化
});

self.addEventListener('activate', (e) => {
  clients.claim(); // 既存タブも新SWに切り替え
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys
        .filter(k => k !== CURRENT_CACHE)
        .map(k => caches.delete(k))
      )
    )
  );
});
```

### アプリ側（更新通知）

```js
navigator.serviceWorker.register('/sw.js').then(reg => {
  reg.addEventListener('updatefound', () => {
    const newSW = reg.installing;
    newSW.addEventListener('statechange', () => {
      if (newSW.state === 'activated') {
        showUpdateBanner(); // 「更新があります」UI表示
      }
    });
  });
});
```

## トラブルシュート: 変更が反映されないとき

1. **DevTools > Network > Disable cache ON** にしてリロード → 変わった？
   - Yes → HTTPキャッシュが犯人。サーバーの`Cache-Control`を見直す
   - No → 次へ
2. **DevTools > Application > Service Workers > Unregister** してリロード → 変わった？
   - Yes → SWキャッシュが犯人。SWのキャッシュ戦略を見直す
   - No → キャッシュではない。サーバー側のコード・ビルドを疑う

この2ステップで犯人を特定できる。「とりあえずプライベートブラウザ」は切り分けにならない。
