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

## 検索例

```bash
# クロダハゼの全配列
grep "kurodai" sequences.tsv

# 特定論文の全サンプル
grep "10.1234/xxx" sequences.tsv

# cytb配列だけ
awk -F'\t' '$3 == "cytb"' sequences.tsv
```
