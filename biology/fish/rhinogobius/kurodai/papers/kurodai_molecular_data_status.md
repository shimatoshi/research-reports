---
tags: [genetics, morphology, taxonomy, taxonomic-confusion]
---

# クロダハゼ *Rhinogobius kurodai* の分子データと分類学的現状

調査日: 2026-04-06

## TL;DR

- GenBankに登録されたR. kurodai名義の配列は30件、実質**8個体・2産地**（東京/三重）のみ
- COI配列は2個体分しかなく、全ゲノムは存在しない（属全体で2種のみ: similis, duospilus）
- タイプ産地（赤坂・黒田侯爵邸の池）は消滅、タイプ標本（1908年）からのDNA抽出は困難
- 再記載（Suzuki & Chen 2011）は**形態のみ**が根拠。分子データは「矛盾しない」程度の補強
- Rhinogobius属全体でmtDNA浸透交雑が報告されており（Yamasaki et al. 2015）、mtDNAベースの種境界判定には限界がある

## 詳細

### 分類史

| 年 | 出来事 | 根拠 |
|---|------|------|
| 1908 | 田中茂穂が *Ctenogobius kurodai* として原記載 | 形態のみ。タイプ産地: 東京赤坂、黒田長礼侯爵邸の淡水池 |
| — | 「トウヨシノボリ」(sp. OR) に紛れ、有効種として認識されない時期が続く | — |
| 2011 | Suzuki & Chen がタイプ標本を再検討し再記載 | 形態のみ |
| 2013 | Akihito et al. の日本産魚類検索図鑑に掲載 | 形態のみ |
| 2015 | Yamasaki et al. が分子系統解析に含める | mt3遺伝子 + 核6遺伝子（部分配列） |

### タイプ標本とタイプ産地

- **ホロタイプ**: ZUMT 2008（東京大学総合研究博物館）、33.9 mm SL
- **パラタイプ**: ZUMT 2009（10個体、20.6-28.9 mm SL）
- **タイプ産地**: 東京赤坂、黒田長礼侯爵邸の淡水池（1908年採集）
- **現状**: 黒田邸跡地は衆議院赤坂議員宿舎・赤坂溜池タワー等に変わっており、**池は消滅**
- **DNA抽出の可能性**: 117年前のホルマリン固定標本からのDNA抽出は技術的に極めて困難

タイプ産地の集団は絶滅した可能性が高い。現在「kurodai」として扱われている個体は、タイプ標本との形態的一致を根拠に同定されたものであり、遺伝的連続性は証明されていない。

### GenBank登録配列の全容

「Rhinogobius kurodai」名義で登録された配列49件のうち、本種の配列は約30件。残りは宿主として記載された寄生虫（Myxobolus, Genarchopsis, Metagonimus, Urorchis）の配列。

#### 個体別データ

| 個体ID | 標本番号 | 産地 | 遺伝子 | 論文 |
|--------|---------|------|--------|------|
| KU-TK100705-1 | NSMT:P:120844 | 東京, 新宿御苑 | CO1, cytb, ND5, E3, sreb2, RAG2, Ptr, RYR3, myh6 | Yamasaki et al. 2015 |
| KU-TK100705-2 | NSMT:P:120845 | 東京, 新宿御苑 | CO1, cytb, ND5, E3, sreb2, RAG2, Ptr, RYR3, myh6 | 同上 |
| KU-TK100705-3 | NSMT:P:120846 | 東京, 新宿御苑 | E3, sreb2, RAG2, Ptr, RYR3, myh6（核のみ） | 同上 |
| haplotype OR01 | KPM-NI:31165 | 三重, 鈴鹿 | ND5 | Mukai et al. 2012 |
| haplotype OR02 | KPM-NI:31160 | 三重, 鈴鹿 | ND5 | 同上 |
| haplotype OR03 | KPM-NI:31172 | 三重, 鈴鹿 | ND5 | 同上 |
| KN1468 | CBM:ZF24322 | 東京 | cytb | Tsuji et al. 2025 |
| D403 | — | 東京 | cytb, 12S | Nakamura et al. 未公刊 |

**合計: 8個体、2産地（東京・三重）、最大9遺伝子領域（mt3+核6）の部分配列**

#### 遺伝子別のカバレッジ

| 遺伝子 | 種類 | 長さ | 個体数 | 産地 |
|--------|------|------|--------|------|
| CO1 | mt | 638 bp | 2 | 東京のみ |
| cytb | mt | 836-1,178 bp | 4 | 東京のみ |
| ND5 | mt | 923-965 bp | 5 | 東京+三重 |
| 12S rRNA | mt | 841 bp | 1 | 東京のみ |
| E3 | 核 | 842 bp | 3 | 東京のみ |
| sreb2 | 核 | 870 bp | 3 | 東京のみ |
| RAG2 | 核 | 882 bp | 3 | 東京のみ |
| Ptr | 核 | 636 bp | 3 | 東京のみ |
| RYR3 | 核 | 806 bp | 3 | 東京のみ |
| myh6 | 核 | 719 bp | 3 | 東京のみ |

全遺伝子合計で約7,500 bp。全ゲノム（数億bp）とは桁違いに少ない。

### 旧名で登録されている関連配列

以下はkurodai検索にヒットしたが、旧名で登録されている配列。現在のkurodaiに含まれるかは論文の確認が必要。

| 登録名 | 遺伝子 | accession | 本数 |
|--------|--------|-----------|------|
| Rhinogobius sp. BF | ND5 | AB753781-782 | 2 |
| Rhinogobius sp. TO | ND5 | AB753783-786 | 4 |
| Rhinogobius sp. BW | ND5 | AB753787-789 | 3 |

これらは Mukai et al. 2012 由来。sp. ORは「トウヨシノボリ」の旧通称であり kurodai に対応するとされるが、sp. TO/BW/BF の帰属は未確認。

### 全ゲノムの状況

Rhinogobius属で参照ゲノムアセンブリが存在する種:

| 種 | ゲノム | 備考 |
|---|--------|------|
| *R. similis*（シマヨシノボリ） | GCA_019453435.1 | 存在する |
| *R. duospilus*（中国産） | 1,031 Mb, 22染色体対 | 2025年公開、高品質（PacBio HiFi + Hi-C） |
| *R. kurodai*（クロダハゼ） | **なし** | |

属83種以上のうち全ゲノムがあるのは2種のみ。

### mtDNA浸透交雑の問題

Yamasaki et al. (2015) は日本産Rhinogobiusのほぼ全種でmtDNAの浸透交雑（introgression）を報告した。これは:

- mtDNA（CO1, cytb, ND5等）は種の境界を正しく反映しない可能性がある
- 形態的に別種でもmtDNAが交雑由来で一致する、あるいはその逆がありうる
- 核DNAによる検証が不可欠だが、kurodaiの核配列は新宿御苑3個体のみ
- 旧名サンプル（sp. TO/BW/BF）には核配列データがない

### 参考: Lefua nishimurai（レイホクナガレホトケドジョウ）の記載手法

Katayama & Sawada (2024) による新種記載は、少ないサンプルからの記載の参考事例:

- 遺伝子: **核S7サブユニット1遺伝子のみ**（452 bp）
- 配列取得: 9個体
- 種内距離: 0.10%、最近縁種との距離: 7.81%（**ギャップ約80倍**）
- 手法: ML系統樹 + ベイズ系統樹 + 統計的パーシモニーネットワーク + K2P距離 + 形態PCA + ランダムフォレスト判別分析
- mtDNAを避けた理由: ナガレホトケドジョウ類でもmtDNA浸透交雑が知られるため

明確なバーコーディングギャップがあれば、1遺伝子・少数サンプルでも種記載が成立することを示す事例。ただし、kurodaiではこのようなギャップの有無自体がまだ検証されていない。

## 自分のプロジェクトへの影響・活用

### species-db Phase 0 への影響

1. **「3点セット」（深度合成写真+位置情報+塩基配列）は既存データの収集では揃わない**。写真と配列が同一個体で紐付けられた記載論文は存在しない
2. **配列データの出発点は確保できた**。sequences.tsv に30件を記入済み
3. **種の境界自体が分子的に不十分**。kurodaiを基準種として分析を始めたが、その基準自体が形態定義に依存している

### 次のステップ候補

1. 手持ちのND5配列で確定kurodai（東京+三重）と旧名サンプル（sp. BW/TO/BF）の距離を算出する（mtDNAの限界を承知の上で）
2. Mukai et al. 2012, Yamasaki et al. 2015 の論文本文を入手し、採集地・標本情報・系統樹の詳細を補完する
3. 博物館DB（NSMT, KPM, CBM）で標本写真のオンライン公開有無を確認する
4. R. similis の参照ゲノムを利用して kurodai の部分配列をマッピングし、ゲノム上の位置を特定する

## 出典

- [Yamasaki et al. 2015 - Mol. Phylogenet. Evol. 90:20-33](https://pubmed.ncbi.nlm.nih.gov/25929788/) — kurodaiを含むRhinogobius属の分子系統。mt+核の多遺伝子解析。mtDNA浸透交雑を報告
- [Mukai et al. 2012 - Bull. Biogeogr. Soc. Jpn. 67:15-24](https://ci.nii.ac.jp/naid/120006342197) — 三重県鈴鹿のため池におけるkurodaiの分布と系統解析
- [Tsuji et al. 2025 - Mol. Ecol.](https://doi.org/10.1111/mec.70059) — 環境DNA比較系統地理。kurodai cytb配列を含む
- [Katayama & Sawada 2024 - Evol. Syst. 8:247-260](https://doi.org/10.3897/evolsyst.8.131002) — Lefua nishimurai新種記載。核1遺伝子+形態による統合分類の参考事例
- [Suzuki et al. 2020 - Bull. Kanagawa Pref. Mus. 49:7-28](https://www.jstage.jst.go.jp/article/bkpmnh/2020/49/2020_2/_article) — R. yaima, R. yonezawai新種記載。写真+座標+形態の記載論文の参考事例
- [R. similis genome - NCBI](https://www.ncbi.nlm.nih.gov/datasets/genome/GCA_019453435.1/) — Rhinogobius属の参照ゲノム
- [R. duospilus genome - G3 Journal](https://academic.oup.com/g3journal/advance-article/doi/10.1093/g3journal/jkaf278/8325495) — Rhinogobius属の高品質ゲノム（2025年）
- [WoRMS - R. kurodai](https://www.marinespecies.org/aphia.php?p=taxdetails&id=1495478) — 分類情報
- [NCBI GenBank - R. kurodai](https://www.ncbi.nlm.nih.gov/nuccore/?term=Rhinogobius+kurodai) — 配列データベース
