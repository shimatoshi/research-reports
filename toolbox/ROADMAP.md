# Toolbox 開発ロードマップ

フィールドワークと生物調査を支援するツール群。

データベース・同定支援の計画は → [`biology/fish/species-db-plan.md`](../biology/fish/species-db-plan.md)

## ツール一覧

### focus-stacking（深度合成）

複数枚の異なる焦点距離の写真を合成し、被写界深度の深い1枚を生成する。

- 画像群の位置合わせ（alignment）
- 各画像からのフォーカス領域抽出
- 合成・ブレンド処理
- バッチ処理対応

技術候補: OpenCV (Laplacian ピラミッド等)、既存OSSの活用 (enfuse, Helicon Focus CLI等)

## 既存ツール

| ツール | 状態 | 概要 |
|--------|------|------|
| `adb-pilot/` | 稼働中 | Android端末の遠隔操作 |
| `browser-save/` | 稼働中 | Webページの保存・クロール |

## 汎用テクニック

| ドキュメント | 概要 |
|-------------|------|
| [dev-mode-cache-bypass.md](dev-mode-cache-bypass.md) | SW・キャッシュ無効化の開発モードパターン（サーバー側制御） |
| [playwright-cli-ui-debug.md](playwright-cli-ui-debug.md) | CLIからブラウザUIを操作・デバッグする方法 |
