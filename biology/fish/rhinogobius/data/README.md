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

## rhinogobius_rag2.fasta

Yamasaki et al. (2015) が GenBank に登録した Rhinogobius 属の核 RAG2 遺伝子配列。82配列、21種/型。
DOI: 10.1016/j.ympev.2015.04.012

NCBI Entrez API 経由でダウンロード（検索条件: `Rhinogobius RAG2 Yamasaki`）。

## rag2_distance_matrix.tsv

rhinogobius_rag2.fasta から算出した種/型間のペアワイズ p-distance（%）。

| カラム | 内容 |
|--------|------|
| `species` | 種名または型名 |
| `n` | サンプル数 |
| `intra_avg` | 種内平均距離（%） |
| `intra_max` | 種内最大距離（%） |
| 以降 | 各種/型との種間平均距離（%） |

## 検索例

```bash
# クロダハゼの全配列
grep "kurodai" sequences.tsv

# 特定論文の全サンプル
grep "10.1234/xxx" sequences.tsv

# cytb配列だけ
awk -F'\t' '$3 == "cytb"' sequences.tsv
```
