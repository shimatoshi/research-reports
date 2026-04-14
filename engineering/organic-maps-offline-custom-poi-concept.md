---
tags: [mapping, offline-maps, organic-maps, comaps, poi, personal-project, concept]
---

# オフライン地図アプリの自作 / Organic Maps拡張案（構想メモ）

調査日: 2026-04-14

## TL;DR

- Organic Maps にはカスタムレイヤー機能がない（Issue #2668 で要望は出ているが 2022/6 から未実装）。地理院タイルを直接差し込むのは既存機能では不可。
- オフライン前提で航空写真・ストリートビューを日本全国確保すると TB 級になり非現実的。代わりに **POI に紐づけた高圧縮 WebP 写真 + テキスト** で詳細補填する方式が筋がいい（全国 50 万 POI × 3 枚で約 30GB）。
- Organic Maps の KML ブックマーク詳細は **HTML レンダリングに対応済み**（表・画像表示あり）。`<description>` に `<img>` を埋めればソース改変ゼロで写真付き POI を並べられる。**これがまず試すべきレベル1**。
- 足りなければソースフォーク（レベル2、Kotlin/Swift 層のみ）で POI 詳細画面に独自写真 DB を追加。C++ 描画エンジンには触らない。
- **重要**: 2025 年に Organic Maps はガバナンス問題でコミュニティ主導の **CoMaps** にフォークされた。個人開発でフォーク元として使うなら、より community-friendly な CoMaps (codeberg.org/comaps/comaps) を選ぶのが妥当。

## 詳細

### 1. 前提となった検討の経緯

#### 1-1. Organic Maps のカスタムレイヤー機能の不在

- Organic Maps はベクタデータ（OSM）をオフラインで端末描画する方式で、タイルサーバから画像を取ってきて重ねるアーキテクチャではない。
- カスタムレイヤー追加の Issue は #2668（"BLM/ESRI maps custom layer addition"、2022/6/4 起票）として残っているが、未実装のまま。
- したがって「地理院タイルをレイヤーとして差し込む」は既存機能では不可能。

#### 1-2. 自作方向の王道

Organic Maps を無理に改造するより、**MapLibre GL JS / Leaflet + 地理院タイル**で新規に組むのが素直。

- 地理院タイル URL: `https://cyberjapandata.gsi.go.jp/xyz/{std|pale|seamlessphoto}/{z}/{x}/{y}.{png|jpg}`
- 利用規約: リアルタイム読み込みなら**出典明示のみで申請不要**。ただし「サーバに過度な負荷をかける通信はアクセス遮断あり」「大量ダウンロードや基本測量成果の利用は事前相談推奨」。

#### 1-3. オフライン前提の容量の壁

オフライン化するとラスタタイルの容量が現実的でなくなる。

| ズーム | 実用感 | 日本全国タイル数（推定） | 容量（航空写真 JPG、15-25KB/枚） |
|---|---|---|---|
| z=12 | 街区が見える | 約16万枚 | 約3〜4 GB |
| z=14 | 建物の塊 | 約260万枚 | 約50〜60 GB |
| z=16 | 建物1軒 | 約4000万枚 | 約800 GB〜1 TB |
| z=18 | Google並み | 約6億枚 | 約10 TB超 |

ストリートビューのオフライン化は Google が商用 API 前提で商用利用不可、Mapillary もバルクダウンロード禁止でそもそも不可能。

### 2. 到達した構想の核：POI + 高圧縮写真方式

#### 2-1. 発想

人間が場所を認知するには、360° パノラマより**代表的な 3〜5 枚の写真 + テキスト**で十分、という観察に基づく。ラスタタイル（全画面を等解像度で保存）は情報密度的に無駄が多い。

#### 2-2. 容量試算

WebP q40 で圧縮した場合の想定：

- 400×300px → 約 15 KB/枚
- 800×600px → 約 40 KB/枚

| 構成 | 容量 |
|---|---|
| 全国の主要観光地・駅・ランドマーク（5万箇所 × 5枚 × 20KB） | **約 5 GB** |
| 飲食店含む全国 POI（50万箇所 × 3枚 × 20KB） | **約 30 GB** |
| 全国 POI ガッツリ（100万箇所 × 5枚 × 20KB） | **約 100 GB** |

ベクタ地図本体（〜1GB）と合わせても、**10GB 前後で「日本全国オフライン地図 + 写真データベース」が成立する**。これは航空写真 z=14 (60GB) より軽く、用途上はるかに有用。

### 3. データソースの整理

写真・テキストの調達元。技術より**ここがボトルネック**。

| ソース | 使える？ | 備考 |
|---|---|---|
| OpenStreetMap | △ | POI 座標は豊富だが写真・レビューはほぼ無い |
| Wikipedia / Wikimedia Commons | ◎ | ランドマーク・観光地に強い。**CC-BY-SA、再配布OK** |
| Wikivoyage | ○ | 観光地の構造化テキスト、オープンライセンス |
| Mapillary | ○ | 街頭写真、CC-BY-SA 4.0。API 経由で利用可、ロゴ表示+リンクバック必須。バルク DL 禁止 |
| 食べログ / ぐるなび | ✕ | 規約違反、スクレイピング不可 |
| Google Places API | △ | 有料、キャッシュ制限、再配布不可 |
| Hot Pepper / ぐるなび API | △ | 個人キー取得可、再配布・ローカル保存は制限あり |
| Foursquare | ○ | 無料枠、日本カバレッジそこそこ |
| **パーソナル収集** | ◎ | 自分で撮って溜める「パーソナル Mapillary」。ライセンス問題ゼロ、品質高 |

**「観光ガイド」方向**: Wikipedia + Wikimedia + Wikivoyage + OSM で完全オープンに完結する。これが最初に試すべき具体案。

**「飯屋ガイド」方向**: 規約の壁が厚く、公開データだけでは作れない。自分で食べ歩いて撮る運用なら逆に問題なし、むしろ品質高い地図になる可能性すらある。

### 4. Organic Maps への載せ方（3段階）

#### レベル1: 既存機能で実現（ソース改変ゼロ）

**Organic Maps の KML ブックマーク詳細は既に HTML レンダリングに対応済み**（表・画像表示の改善ニュースあり）。したがって、

```xml
<Placemark>
  <name>店名</name>
  <description><![CDATA[
    <img src="file:///storage/emulated/0/photos/xxx.webp" width="400"/>
    <p>店の説明テキスト</p>
  ]]></description>
  <Point><coordinates>139.7,35.6,0</coordinates></Point>
</Placemark>
```

のような KML を「ブックマークカタログ」としてインポートすれば、POI タップで写真 + 説明が出る。

加えて、**Organic Maps は Wikipedia 連携を標準搭載**：
- OSM の `wikipedia=*` タグを読み、該当記事を表示
- `wikiparser` ツールで Wikipedia 記事を mwm ファイルにオフライン埋め込み（Google Summer of Code 2022-2023 成果）
- **ただし最近はイントロのみ表示でブラウザ誘導に退化した**との報告あり（Issue #3052）

→ レベル1 の組み合わせだけで**要件の 80% を実現可能**な可能性が高い。まずここで検証すべき。

#### レベル2: ソースフォーク（Kotlin/Swift 層のみ改変）

- リポジトリ: https://github.com/organicmaps/organicmaps （もしくはフォーク先 https://codeberg.org/comaps/comaps ）
- 構成: C++ コア（描画・データ） + Kotlin/Swift（UI 層）
- 作業:
  1. 独自 POI-写真 DB（SQLite or sidecar file）を `assets/` に同梱
  2. POI 詳細画面に「写真ギャラリー」タブを追加（Kotlin / Swift だけで済む）
  3. 座標・POI ID から DB を引く
- ビルド: Android Studio + NDK で公式手順通り。`docs/` にビルド手順あり。
- **C++ 描画パイプライン（drape_frontend）には手を入れない**。UI 層だけで目的達成できる。

#### レベル3: 描画エンジン改造（非推奨）

- C++ drape_frontend にラスタレイヤー描画を追加する試み。
- OSM ベクタ描画の前提と噛み合わず、茨の道。レベル2で目的達成できるので**やる意味がない**。

#### ライセンス・商標

- **Apache License 2.0**: 改変・再配布 OK
- **「Organic Maps」の名前・ロゴは Estonia 登録の Organic Maps OÜ が商標保有**。自作ビルドを配る場合はリネーム必須（README に明記）。
- 個人利用（自分の端末にインストールして使うだけ）なら商標問題なし。

### 5. CoMaps フォーク状況（2025-2026 の重要トピック）

Organic Maps はガバナンス問題で 2025 年春に分裂、**CoMaps** というコミュニティ主導フォークが発足している。

- 2025/6/1: 最初の Android APK プレビュー公開
- 2025/7: iOS / Android の公式ストア配信開始
- 2026/1 末: Linux 版 Flathub 配信開始
- 活発な開発: 1,200+ PR マージ、30+ 開発者、50 言語対応
- マップ生成サーバ刷新で生成時間 11日→2日に短縮
- 原則: Transparency / Community decision-making / Not-for-profit / Privacy-focused
- リポジトリ: https://codeberg.org/comaps/comaps

**個人開発でフォークして拡張する目的なら、CoMaps を base にする方が望ましい**可能性が高い：
- ガバナンスが community-led で PR マージの見通しが立てやすい
- 商標問題の再発を避けるため、そもそもリネーム前提で設計されている
- 開発速度が上がっており技術的に追従しやすい

### 6. ロードマップ

```
1週目: 特定エリア（例: 地元 or 旅行予定地）の POI 10〜30 件分を
       Wikipedia/Wikimedia Commons から画像収集 → WebP q40 圧縮
       → KML に <description><img> で埋め込み → Organic Maps にインポート
       （レベル1 の検証）

2〜4週目: 足りなければ CoMaps をフォーク → Android Studio でビルド通す
       → POI 詳細画面に写真ギャラリータブ追加（レベル2）

5週目以降: Wikipedia 日本語版の位置情報付き記事 + Commons 画像を
       バルク取得するパイプラインを自作
       → 全国観光地スポット数万箇所を数GB のオフライン DB 化
```

## 自分のプロジェクトへの影響・活用

個人開発の構想メモのため、本業（SR-APP screen 実装）との直接の関係はない。ただし以下の副次的な接続がある：

- Figma → React の UI 実装経験は、Organic Maps の Kotlin 層（レベル2）を触る際の UI 改修スキルと近い
- モノレポ + Docker ビルドの知見は、CoMaps のような大規模 OSS プロジェクトをビルド環境から立ち上げる際に役立つ

本業で疲れた時の気分転換プロジェクトとして、レベル1（KML インポート）から着手するのが現実的。

## 出典

- [BLM/ESRI maps custom layer addition · Issue #2668](https://github.com/organicmaps/organicmaps/issues/2668) — カスタムレイヤー要望、2022/6 起票・未実装
- [Organic Maps FAQ - How to import bookmarks](https://organicmaps.app/faq/bookmarks/how-to-import/) — KML/KMZ/GPX/GeoJSON 対応
- [Organic Maps May 2024 update news](https://organicmaps.app/news/2024-05-19/the-may-2024-organic-maps-update-bookmarks-and-tracks-sorting-by-name-gpx-fixes/) — ブックマーク詳細の HTML（表・画像）レンダリング改善
- [organicmaps/wikiparser GitHub](https://github.com/organicmaps/wikiparser) — Wikipedia オフライン埋め込みツール
- [Bring back the full Wikipedia articles · Issue #3052](https://github.com/organicmaps/organicmaps/issues/3052) — Wikipedia 表示がイントロのみに退化
- [Organic Maps terms (Apache 2.0 / trademark)](https://organicmaps.app/terms/) — ライセンスと商標
- [CoMaps - community-led fork](https://www.comaps.app/news/2025-05-12/3/) — 2025/5 フォーク宣言
- [CoMaps end of 2025 status](https://www.comaps.app/news/2025-12-16/comaps-and-its-community-end-of-2025/) — 開発状況サマリ
- [CoMaps codeberg repo](https://codeberg.org/comaps/comaps) — CoMaps ソース
- [CoMaps emerges as Organic Maps fork - LWN](https://lwn.net/Articles/1024387/) — 分裂経緯の解説
- [地理院タイル利用規約（国土地理院）](https://maps.gsi.go.jp/help/termsofuse.html) — リアルタイム読み込みは出典明示のみで申請不要、サーバ負荷は遮断対象
- [地理院タイル一覧](https://maps.gsi.go.jp/development/ichiran.html) — タイル種別・ズーム範囲
- [Mapillary CC-BY-SA license](https://help.mapillary.com/hc/en-us/articles/115001770409-CC-BY-SA-license-for-open-data) — 画像ライセンス
- [Mapillary Terms of Use](https://www.mapillary.com/terms) — API 利用条件、ロゴ表示・リンクバック必須
