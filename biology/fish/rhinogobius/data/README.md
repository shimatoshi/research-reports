# data/

Rhinogobius sp. OR複合体の分子データ・個体情報。2層構造で管理。

## specimens.tsv（個体マスタ）

1行 = 1個体（物理的な標本）。配列・形態・生態・引用の全情報がここに紐づく。

| カラム | 内容 | 空欄の意味 |
|--------|------|-----------|
| `specimen_id` | 個体識別子。Yamasaki2015はisolateコード、その他は論文固有ID | — |
| `taxon_genbank` | GenBank登録時の学名（そのまま転記） | — |
| `taxon_current` | 現在の分類学的位置づけ（例: sp.BF → R. tyoni） | 未検討 |
| `morphotype` | 形態型: 橙色型/宍道湖型/偽橙色型/縞鰭型/沼型/房総型 等 | 不明 |
| `life_history` | 生活史型: 両側回遊/湖河回遊/淡水定住/陸封/陸封(非在来) | 不明 |
| `locality` | GenBank geo_loc_name（原文） | — |
| `prefecture` | 都道府県 | — |
| `river_system` | 水系名 | 不明 |
| `habitat_type` | 河川/池/ダム湖/湖/水路/ため池 | 不明 |
| `collection_date` | 採集日（YYYY-MM-DD） | 不明 |
| `specimen_voucher` | 標本番号（NSMT:P:, CBM:ZF:, KPM-NI: 等） | 未登録 |
| `body_size_mm` | 体長SL (mm) | データなし |
| `egg_size_mm` | 卵径 (mm) | データなし |
| `otolith_srca` | 耳石Sr:Ca比の結果（amphidromous/freshwater等） | 未分析 |
| `sex` | 性別 | 不明 |
| `cited_in` | 言及されている論文（セミコロン区切り） | — |
| `figure_table` | 論文内のFigure/Table番号 | 不明 |
| `notes` | 補足 | — |

## sequences.tsv（配列テーブル）

1行 = 1 GenBankアクセッション番号。`specimen_id`で個体マスタに紐づく。

| カラム | 内容 |
|--------|------|
| `accession` | GenBank/DDBJアクセッション番号 |
| `specimen_id` | → specimens.tsv の specimen_id |
| `gene` | 遺伝子領域名: CO1, cytb, ND5, 12S, 16S, control_region, RAG2, E3, sreb2, Ptr, RYR3, myh6, microsatellite |
| `genome` | mt (ミトコンドリア) / nuc (核) |
| `length_bp` | 配列長 (bp) |
| `paper_doi` | 出典論文のDOI |
| `paper_short` | 出典の略称（Yamasaki2015, Tsuji2025 等） |
| `genbank_organism` | GenBank登録時の organism name（原文） |
| `notes` | 補足 |

## 旧ファイル

- `sequences_old.tsv` — 再設計前の1層構造（バックアップ）

## 設計原則

- **個体が軸**。同一個体の全遺伝子が specimen_id で串刺しできる
- **空欄 = 未知**。論文に戻って補完するための導線が paper_doi と cited_in にある
- **GenBank名と現在の分類を分離**。taxon_genbank（事実）と taxon_current（解釈）を区別する
- **配列領域が明確**。gene + genome + length_bp で何の配列かわかる

## FASTA配列ファイル

| ファイル | 内容 | 配列数 |
|--------|------|--------|
| `rhinogobius_rag2.fasta` | RAG2 全種 (Yamasaki 2015) | 82 |
| `rhinogobius_E3.fasta` | E3 全種 | 82 |
| `rhinogobius_sreb2.fasta` | sreb2 全種 | 82 |
| `rhinogobius_Ptr.fasta` | Ptr 全種 | 82 |
| `rhinogobius_RYR3.fasta` | RYR3 全種 | 82 |
| `rhinogobius_myh6.fasta` | myh6 全種 | 82 |
| `sp_or_cytb_tabata2016.fasta` | 琵琶湖 cytb 15ハプロ | 15 |
| `sp_or_dloop_akihito2019.fasta` | 琵琶湖 D-loop 24個体 | 24 |

## 検索例

```bash
# ある個体の全配列を取得
grep "OR-NI110816-1" sequences.tsv

# 回遊型個体だけ抽出
awk -F'\t' '$5 == "両側回遊"' specimens.tsv

# sp.BFの産地一覧
awk -F'\t' '$2 ~ /sp\. BF/' specimens.tsv | cut -f6

# cytbだけの配列リスト
awk -F'\t' '$3 == "cytb"' sequences.tsv
```
