# ハゼ類 (Gobiiformes) 総合リサーチデータセット

**生成日:** 2026-04-17 / **用途:** オフライン閲覧用リファレンス
**対象読者:** 在野研究者 (Rhinogobius 属研究が主)

日本産および東アジアハゼ類について、分類・生態・形態・保全・研究史を網羅した Markdown データセット。全章は一次文献 DOI 付き、画像は Wikimedia Commons 等の CC/PD ライセンス素材のみ。

---

## 章構成 (推奨閲覧順)

| # | ファイル | 内容 | 字数目安 |
|---|---|---|---|
| 01 | [01-taxonomy-phylogeny.md](01-taxonomy-phylogeny.md) | Gobiiformes 目の高次分類・分子系統 (Thacker, Tornabene, McCraney 系列)・科の再編 (Oxudercidae 分立) | ~1,600 語 |
| 02 | [02-japanese-goby-species-catalog.md](02-japanese-goby-species-catalog.md) | 日本産ハゼ 15 属グループの種別カタログ (学名/和名/分布/生息地/保全) | ~15,000 字 |
| 03 | [03-rhinogobius-deep-dive.md](03-rhinogobius-deep-dive.md) | **Rhinogobius 属深掘り**。記載史・全種リスト・分子系統・陸封化・外来種問題 | ~4,500 字 |
| 04 | [04-ecology-life-history.md](04-ecology-life-history.md) | 両側回遊・産卵・浮遊仔魚・食性・共生・洞窟/干潟/深海適応 | ~23,400 字 |
| 05 | [05-morphology-identification.md](05-morphology-identification.md) | 同定形質ガイド: 感覚孔系・鰭条計数・鱗・生殖突起・斑紋・骨格・用語対応表 | ~2,100 語 |
| 06 | [06-conservation.md](06-conservation.md) | 環境省 RL2020・IUCN・地方版 RDB・脅威・保全事例 | ~12,700 字 |
| 07 | [07-research-history.md](07-research-history.md) | 日本 (明仁上皇・鈴木寿之・渋川浩一・瀬能) と世界 (Miller, Murdy, Thacker, Kottelat, Chen) の研究者系譜 | ~1,540 語 |

---

## 画像アーカイブ

`images/` に 50 枚 WebP (合計 **32 MB**、旧 JPG 93 MB から 66% 圧縮)、18 種を網羅。
全画像のライセンス・著者・撮影地は **[images/MANIFEST.md](images/MANIFEST.md)** 参照。

### 代表画像

#### Rhinogobius 属 (ヨシノボリ属) — ユーザ研究主対象

| 種 | 画像 |
|---|---|
| カワヨシノボリ *R. flumineus* | ![R. flumineus](images/rhinogobius_flumineus_01.webp) |
| オオヨシノボリ *R. nagoyae* | ![R. nagoyae](images/rhinogobius_nagoyae_01.webp) |
| クロヨシノボリ *R. kurodai* | ![R. kurodai](images/rhinogobius_kurodai_01.webp) |
| ビワヨシノボリ *R. biwaensis* | ![R. biwaensis](images/rhinogobius_biwaensis_01.webp) |
| シマヨシノボリ *R. brunneus* complex | ![R. brunneus cobalt](images/rhinogobius_brunneus_cobalt.webp) |
| ゴクラクハゼ系 *R. similis* | ![R. similis](images/rhinogobius_similis_01.webp) |

#### その他日本代表ハゼ

| 種 | 画像 |
|---|---|
| マハゼ *Acanthogobius flavimanus* | ![マハゼ](images/acanthogobius_flavimanus_01.webp) |
| ウキゴリ *Gymnogobius urotaenia* | ![ウキゴリ](images/gymnogobius_urotaenia_01.webp) |
| イサザ *G. isaza* (琵琶湖固有・EN) | ![イサザ](images/gymnogobius_isaza_01.webp) |
| チチブ *Tridentiger obscurus* | ![チチブ](images/tridentiger_obscurus_01.webp) |
| ヌマチチブ *T. brevispinis* | ![ヌマチチブ](images/tridentiger_brevispinis_01.webp) |
| ミミズハゼ *Luciogobius guttatus* | ![ミミズハゼ](images/luciogobius_guttatus_01.webp) |
| ボウズハゼ *Sicyopterus japonicus* | ![ボウズハゼ](images/sicyopterus_japonicus_01.webp) |
| ムツゴロウ *Boleophthalmus pectinirostris* | ![ムツゴロウ](images/boleophthalmus_pectinirostris_01.webp) |
| トビハゼ *Periophthalmus modestus* | ![トビハゼ](images/periophthalmus_modestus_01.webp) |
| ドンコ *Odontobutis obscura* | ![ドンコ](images/odontobutis_obscura_01.webp) |
| カワアナゴ *Eleotris oxycephala* | ![カワアナゴ](images/eleotris_oxycephala_01.webp) |
| ルリボウズハゼ系 *Stiphodon* | ![Stiphodon](images/stiphodon_atropurpureus_01.webp) |

---

## 横断的メモ (章をまたぐ論点)

### 1. 科レベル分類の揺らぎ (01章 ↔ 03章)
- Nelson et al. 2016 以降、Gobiidae から **Oxudercidae** を分立する 2 科体系が主流化。Rhinogobius は Oxudercidae: Gobionellinae に置かれる。
- ただし Thacker 系列の一部論文や Nakabo 2013 は 1 科 + 亜科制を維持。**引用時はソースの時代・体系を明示すること**。

### 2. Rhinogobius mizunoi 記載年の矛盾
- 03章レポートは Suzuki, Shibukawa & Aizawa **2017** とする (複数ソース一致)。
- ユーザのメモ (`project_rhinogobius_phase.md`) には「2020」とあるため、**要再確認 → 原記載 PDF での突き合わせ必要**。

### 3. 未記載種の便宜名マッピング
- `Rhinogobius sp. BB / BF / BI / DA / DL / CB / CO / OM / TO / YB / MO / KZ` 等の便宜名は情報源ごとに揺れあり。
- 鈴木寿之氏の最新レビュー + 原記載論文での再確認が推奨される (07章末に追跡フロー記載)。

### 4. 画像の同定注意
- Commons 上のファイル名と和名キャプションが不一致の例あり (例: `Rhinogobius_nagoyae_Nakagawa.webp` がシマヨシノボリとして投稿)。`images/MANIFEST.md` に個別注記済。Rhinogobius 改訂の進行中ゆえ。

### 5. 環境省レッドリスト現状 (06章)
- 2026-04 時点では **RL2020 が最新**。第5次 (汽水・淡水魚類) は 2026 年度以降予定。
- 一次 PDF がバイナリで未抽出の項目あり — 次の作業候補。

---

## オフライン再現・更新の手順

```bash
cd /home/kobayashi-takeru/work/shimatoshi/research-reports/biology/fish/gobies-overview/
# 章を読む
less 03-rhinogobius-deep-dive.md
# 画像を開く
xdg-open images/rhinogobius_flumineus_01.webp
# マニフェストで出典確認
less images/MANIFEST.md
```

### 追加作業の候補 (TODO)
- [ ] 環境省レッドリスト 2020 別添資料3 (汽水・淡水魚類全種リスト) の PDF テキスト化
- [ ] *R. telma* の原記載 PDF 入手 + フリー画像なし → 標本写真の自前作成が必要
- [ ] Suzuki & Chen 2011, Suzuki et al. 2015 (タイプ種 neotype 指定) の原著 PDF 入手
- [ ] McDowall 1997 (両側回遊改訂) PDF ダウンロード (04章ソースにリンクあり)
- [ ] iNaturalist research-grade 観察データ CSV 取得 (分布点マッピング用)
- [ ] Rhinogobius 主要 10 種の頬部斑紋クローズアップ写真の追補

---

## ライセンスと出典

- 画像: 全て CC BY / CC BY-SA / Public Domain (Wikimedia Commons)。個別出典は `images/MANIFEST.md`。
- テキスト: 本リポジトリ内部向け。各章末の Sources セクションに一次文献 URL/DOI。

---

## データセット統計

- 総ファイル数: 9 Markdown + 50 画像 (WebP) + 1 Manifest + 10 HTML = **70 ファイル**
- 総容量: **33 MB** (WebP化で 93 MB → 33 MB に圧縮)
- 総文字数 (本文): 約 **200,000 字**
- 引用一次文献: **100+ 件** (各章合算)
- 収録種数: **70+ 種** (日本産中心、東アジア含む)
