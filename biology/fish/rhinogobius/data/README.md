# data/

塩基配列メタデータとサンプル情報。レポート（papers/等）との紐付けはDOIやアクセッション番号で行う。

## sequences.tsv

| カラム | 内容 |
|--------|------|
| `accession` | GenBank/DDBJアクセッション番号 |
| `species` | 種名（フォルダ名と対応: kurodai, nagoyae等。不明なら `sp.` や仮称） |
| `gene` | 遺伝子領域（cytb, COI, RAG1等） |
| `locality` | 採集地 |
| `paper_doi` | 出典論文のDOI |
| `notes` | 補足（旧名、疑義、サンプル状態など） |

## 核DNA配列（Yamasaki et al. 2015）

Yamasaki et al. (2015) が GenBank に登録した Rhinogobius 属の核遺伝子配列。各82配列、21種/型。
DOI: 10.1016/j.ympev.2015.04.012. NCBI Entrez API 経由でダウンロード。

| ファイル | 遺伝子 | 配列長 |
|--------|--------|------|
| `rhinogobius_rag2.fasta` | RAG2 | ~882 bp |
| `rhinogobius_E3.fasta` | E3 | ~842 bp |
| `rhinogobius_sreb2.fasta` | sreb2 | ~870 bp |
| `rhinogobius_Ptr.fasta` | Ptr | ~636 bp |
| `rhinogobius_RYR3.fasta` | RYR3 | ~806 bp |
| `rhinogobius_myh6.fasta` | myh6 | ~719 bp |

## 距離データ

### rag2_distance_matrix.tsv

RAG2 のみの全種/型間ペアワイズ p-distance（%）。

### nuclear_6gene_distances.tsv

全6核遺伝子の種内距離・種間距離のサマリ。

| カラム | 内容 |
|--------|------|
| `comparison` | 種名（intra）またはペア（inter） |
| `type` | intra / inter |
| `RAG2`〜`myh6` | 各遺伝子の p-distance（%） |
| `average` | 6遺伝子の平均距離（%） |

## 検索例

```bash
# クロダハゼの全配列
grep "kurodai" sequences.tsv

# 特定論文の全サンプル
grep "10.1234/xxx" sequences.tsv

# cytb配列だけ
awk -F'\t' '$3 == "cytb"' sequences.tsv
```
