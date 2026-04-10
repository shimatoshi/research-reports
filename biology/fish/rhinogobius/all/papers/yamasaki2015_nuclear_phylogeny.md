---
tags: [phylogeny, nuclear-DNA, mtDNA, life-history, egg-size, speciation, hybridization, biogeography]
---

# Yamasaki et al. (2015) — 日本産Rhinogobius属の核DNA系統・生活史進化・種間交雑

読解日: 2026-04-10
原文: `kurodai/papers/yamasaki2015_phylogeny.pdf`
関連:
- [tou_yoshinobori_complex.md](../../kurodai/papers/tou_yoshinobori_complex.md)
- [rhinogobius_egg_size_and_life_history.md](./rhinogobius_egg_size_and_life_history.md)
- [rhinogobius_dorsal_fin_and_migration.md](./rhinogobius_dorsal_fin_and_migration.md)
- [sp_or_landlocking_and_life_history_diversity.md](./sp_or_landlocking_and_life_history_diversity.md)
- [SPECIES_CRITERIA.md](../../SPECIES_CRITERIA.md)

---

## 書誌情報

Yamasaki YY, Nishida M, Suzuki T, Mukai T, Watanabe K (2015) "Phylogeny, hybridization, and life history evolution of *Rhinogobius* gobies in Japan, inferred from multiple nuclear gene sequences." *Molecular Phylogenetics and Evolution* 90:1-12. DOI: [10.1016/j.ympev.2015.04.012](https://doi.org/10.1016/j.ympev.2015.04.012)

**著者所属**: 京都大学理学研究科（Yamasaki, Watanabe）、東京大学大気海洋研究所（Nishida）、川西緑台高校（Suzuki）、岐阜大学地域科学部（Mukai）

---

## TL;DR

- 日本産Rhinogobius 18種を核DNA 6遺伝子（4755bp）で初めて包括的に系統解析
- 核DNAとmtDNAの系統樹が大きく不一致 → 更新世前期〜中期に大規模な種間mtDNA浸透交雑
- 両側回遊型→淡水型への生活史変化が少なくとも3系統で独立に発生（収斂進化）
- 卵サイズ変化は生活史変化と常にセットで起きる
- **一度淡水型になった種は回遊型に戻れない（不可逆）**
- sp.ORは核DNAで非単系統（AU test p < 0.001）→ kurodai, sp.KZ と分離不能
- sp.BF, sp.BW, sp.OM は sp.OR（回遊型）の祖先から分化した止水型

---

## 1. 方法

### サンプリング
- 96個体（日本産18種 ＋ 大陸種3種: R. giurinus, R. leavelli, R. virgigena）
- 2001〜2013年に本土・琉球列島・小笠原諸島から採集
- 広域分布種は2〜8地点からサンプリング
- 証拠標本: 国立科学博物館（NSMT-P 65160, 65165, 120783-120861）

### 遺伝子
| 区分 | 遺伝子 | 合計塩基対 |
|------|--------|----------|
| mtDNA | CO1, ND5, cytb | 2781 bp |
| 核DNA | myh6, RYR3, Ptr, sreb2, RAG2, EGR3 | 4755 bp |

### 解析手法
- ML（RAxML-7.2.6）、ベイズ（MrBayes 3.2.1）で系統樹推定
- BEAST v1.7.5 で分岐年代推定
- MuSSE モデル（diversitree パッケージ）で祖先状態復元（生活史・卵サイズ）
- AU test（CONSEL）で単系統性の統計的検定

### 分岐年代推定のキャリブレーション
| ポイント | 地質イベント | 年代 |
|---------|-----------|------|
| CA1 | 小笠原諸島の形成 | 0.9-1.8 Mya |
| CA2 | トカラ海峡の開裂（本土-琉球の隔離） | 1.55 ± 0.154 Mya |
| 分子時計 | cytb の進化速度（Gymnogobius準拠） | 3.0%/Myr (95% HPD 0.7-4.8%) |

---

## 2. 核DNA系統樹の構造

### 3大クレード（Fig. 3）

```
                ┌── R. flumineus (fluvial, large egg)
  N-1 ──────────┤
                └── R. sp. TO [= R. telma] (lentic, small egg)

                ┌── R. nagoyae (amphidromous, small egg)
  N-2 ──────────┤
                └── R. sp. CO [= R. mizunoi] (amphidromous, small egg)

                ┌── N-3-1: R. brunneus + sp. YB
  N-3 ──────────┼── N-3-2: R. fluviatilis + R. ogasawaraensis + sp. DL
                └── N-3-3: sp. MO, sp. BB, sp. OR, sp. KZ, R. kurodai,
                           sp. OM, sp. BF, sp. BW
```

### 統計的支持値（核DNA連結データ）

| クレード | BP | PPM | PPB |
|---------|-----|------|------|
| N-1 (flumineus + sp.TO) | 95% | 1.0 | 1.0 |
| N-2 (nagoyae + sp.CO) | -/0.99 | - | - |
| N-3 | 78% | 1.0 | 1.0 |
| N-3-1 (brunneus + sp.YB) | -/0.97 | - | - |
| N-3-2 (fluviatilis + ogasawaraensis + sp.DL) | 83% | 1.0 | 1.0 |
| N-3-3 | - | - | - |

**N-3-3クレード内の分解能は低い。** sp.OR, sp.KZ, R. kurodai, sp.BW, sp.BF, sp.OM 間の関係は未解決。

### sp.ORの非単系統性

- sp.ORの複数サンプルはN-3-3内でR. kurodai, sp.KZと混在して配置される
- **AU test: sp.ORの単系統性は統計的に棄却（p < 0.001）**
- R. fluviatilis の単系統性も棄却（p < 0.001）
- sp.BW は sp.BF と単系統群を形成（BP 70%, PPM 0.53, PPB 0.64 — 弱い支持）

---

## 3. mtDNA系統樹との不一致

### mtDNAのクレード構造（Fig. 2）

| クレード | 含まれる種 | 特徴 |
|---------|---------|------|
| M-1 | R. ogasawaraensis | 最も基盤的 |
| M-2 | sp. BW | 単独 |
| M-3 | sp. TO [= R. telma] | 単独 |
| M-4 | R. flumineus | 単独 |
| M-5 | R. nagoyae（本土） | 本土のみ |
| M-6 | **本土の9種が混合** | 地理的にソート |
| M-7 | **琉球の6種が混合** | 地理的にソート |

### 不一致のパターン

**核DNAでは種ごとに単系統になるのに、mtDNAでは地理的にソートされる。**

- R. nagoyae: 核では単系統 → mtDNAでは本土（M-5）と琉球（M-7）に分裂
- R. brunneus: 核では単系統 → mtDNAでは本土（M-6）と琉球（M-7）に分裂
- AU test: R. nagoyae の単系統性を棄却（mtDNA, p < 0.001）; R. brunneus も棄却（p < 0.001）

**原因: 種間浸透交雑によるmtDNA置換（introgressive hybridization）**

- incomplete lineage sorting ではなく introgression と判断: 後者ならランダムな分布を予測するが、実際は地理的にソートされている
- 時期: R. ogasawaraensis 分岐後の更新世前期〜中期（〜1.59 Mya）
- mtDNA と核DNA の R. ogasawaraensis 分岐年代が一致（1.59 vs 1.55 Myr）→ 大規模浸透交雑の開始時期を支持

### 淡水種はmtDNA浸透を免れている

> "freshwater species, such as *R. flumineus*, *Rhinogobius* sp. TO, *Rhinogobius* sp. BW (the mainland), and a part of *Rhinogobius* sp. BB (Ryukyu), branched out earlier and have retained their independent lineages in the mtDNA phylogeny." (L484-486)

**含意: 回遊型同士よりも、回遊型と淡水型の間の生殖隔離の方が強い。**

理由の推定:
- 回遊型は繁殖場所が重なりやすい（河川中〜下流の瀬）
- 海面変動で河川が短縮すると繁殖場所が強制的に重なる → 交雑
- 淡水型は生息環境（止水域、上流域）が異なるため接触しにくい

---

## 4. 分岐年代の推定

### 核DNA

| ノード | tMRCA (Mya) | 95% HPD |
|--------|-------------|---------|
| 全日本産種（R. giurinus除く） | 4.48 | 2.38-6.66 |
| N-3-2 (fluviatilis + ogasawaraensis + sp.DL) | 1.78 | 1.03-2.53 |
| N-3-3 全体 | 1.65 | 0.81-2.53 |
| R. flumineus + R. sp. TO | 1.43 | 0.49-2.44 |
| **sp.OR + sp.KZ + R.kurodai** vs **sp.MO + sp.BB** | **1.20** | **0.59-1.89** |
| sp.BW + sp.BF + sp.OM | 1.10 | 0.49-1.77 |
| sp.BW + 一部sp.BF | 0.90 | 0.35-1.51 |
| CA2 (R. nagoyae 本土 vs 琉球) | 1.14 | 0.68-1.69 |

### トカラ海峡による分化

3組の本土-琉球ペアの分岐年代がほぼ一致:
1. R. nagoyae: 1.14 Myr
2. N-3-2 (fluviatilis + ogasawaraensis vs sp.DL): 1.78 Myr
3. N-3-3 (sp.OR群 vs sp.MO + sp.BB): 1.20 Myr

→ トカラ海峡の開裂（1.55 Mya）による異所的種分化を支持

### sp.BW（ビワヨシノボリ）の分化時期

sp.BW + 一部sp.BF の tMRCA = 0.90 Myr (0.35-1.51 Myr)

琵琶湖の大規模深水環境の形成（0.4 Mya; Meyers et al. 1993; Kawabe 1994）とおおむね一致。sp.BWは祖先的なlentic型（sp.BF的な種）から琵琶湖の沖合環境に適応して分化したと推定。

---

## 5. 生活史と卵サイズの進化（MuSSE解析）

### 祖先状態

**日本産Rhinogobius全体の祖先は両側回遊型（amphidromous）・小卵型と推定。**

### 生活史変化のパターン（Fig. 4a）

3つの変化パターンが復元された（生活史変化と卵サイズ変化は常にセットで起きる）:

#### パターン1: Amphidromous → Fluvial（小卵→大卵）— 3系統で独立に発生

| 系統 | 祖先（回遊型） | 派生（河川型） | 地域 |
|------|-------------|-------------|------|
| N-1系統 | 不明（基盤的位置） | R. flumineus | 本土西部 |
| N-3-1系統 | R. brunneus | sp. YB | 琉球（八重山） |
| N-3-3系統 | sp. MO | sp. BB | 琉球（沖縄島北部） |

sp.YBの進化: 滝による隔離で並行進化（Kano et al. 2012）
sp.BBの進化: 海面低下時に河川上流に侵入したsp.MO祖先から分化（Kondo et al. 2013）

**R. flumineus の祖先復元は曖昧**: 基盤的位置のため祖先が回遊型か不確実。大陸の大卵型種（Chen et al. 2008）の存在も考慮が必要。

#### パターン2: Amphidromous → Lentic（小卵→やや小さい卵）— 1系統

| 祖先 | 派生 | 地域 |
|------|------|------|
| sp. OR（回遊型） | sp. BF + sp. BW (+ sp. OM) | 瀬戸内海周辺・琵琶湖 |

- 卵サイズの変化は小さい（amphidromous と lentic はどちらも小卵型の範囲内）
- 理由: 両型とも仔魚がプランクトン豊富な止水域（海 or 湖）で育つため、適応的な卵サイズの差が小さい
- **ただし lentic 種は amphidromous 種より体サイズが小さく（矮小化）、小さい体に対してより多くの卵を産む方が有利 → 卵がやや小さくなる**

#### パターン3: Fluvial → Lentic（大卵→小卵への逆戻り）— 1系統

| 祖先 | 派生 | 地域 |
|------|------|------|
| R. flumineus（河川型、大卵） | R. sp. TO [= R. telma]（止水型、小卵） | 伊勢湾周辺 |

- **卵サイズの進化が小→大→小と逆転した唯一の事例**
- sp.TOは鮮新世から存在する伊勢湾地域の湿地環境（古東海湖）に適応
- sp.TOの矮小形態（dwarf morphology）は sp.BF, sp.BW と収斂的に一致（別系統からの独立進化）

### 生活史変化の不可逆性

> "The reconstructed life history changes did not include the changes from freshwater (fluvial or lentic) to amphidromous types." (L586)

**淡水型→回遊型への逆戻りは一例も復元されなかった。**

理由:
1. 回遊型は塩分耐性・降海回遊行動が必要
2. 淡水型の一部（sp.YB, sp.BB）は塩分耐性を喪失している（Hirashima & Tachihara 2000）
3. 淡水適応中に遺伝的変異が失われる（浄化選択 or ボトルネック効果）
4. 既存の回遊型との競争・交雑が逆戻りを阻害

### MuSSEモデルの結果

**最適モデルは最も単純なモデル（種分化・絶滅・形質遷移率が全て状態非依存）。**

つまり、生活史型（amphidromous/fluvial/lentic）による種分化率の差は検出されなかった。ただし:
- 祖先状態の比例尤度は高くない部分がある（59.6-99.9%）
- サンプリングが日本種に偏っているため、大陸種を含めた再検証が必要

---

## 6. 生物地理学的シナリオ

### sp.TO [= R. telma] の起源（Fig. 4b）

R. flumineus の分布域内（伊勢湾地域）に sp. TO が限定分布。fluvial（R. flumineus）→ lentic（sp.TO）の変化は、鮮新世から存在した古東海湖（Paleo-Lake Tokai）の湿地環境への適応と推定。伊勢湾地域には他にも固有種が多い（Pseudorasbora pugnax, Cobitis minamorii tokaiensis 等）。

### sp.BF + sp.BW + sp.OM の起源（Fig. 4c）

瀬戸内海沿岸のsp.ORから、瀬戸内海周辺の止水環境に適応して分化。
- sp.BF: 瀬戸内海周辺の湿地・ため池
- sp.BW: 琵琶湖の沖合環境
- sp.OM: 琵琶湖流入河川・沿岸域

更新世に瀬戸内海地域に大規模な淡水系が存在（第二瀬戸内海; Yokoyama & Nakagawa 1991）。sp.BWの分化時期（0.90 Myr）は琵琶湖の深水化（0.4 Mya）と概ね一致。

### R. ogasawaraensis の起源（Fig. 4d）

核DNAで R. fluviatilis の姉妹種。R. brunneus との体色類似は収斂。本土から1000km離れた海洋島（小笠原）への分散は例外的イベント（ヨシノボリ仔魚は沿岸帯にとどまり外洋を渡らない）。

### N-3-3の本土-琉球分化（Fig. 4e）

sp.OR + sp.KZ + R.kurodai（本土）vs sp.MO + sp.BB（琉球）の分岐 = 1.20 Myr。トカラ海峡の開裂による分化。

---

## 7. 種間交雑の歴史

### 大規模mtDNA浸透交雑のシナリオ

1. R. ogasawaraensis の分岐（〜1.59 Mya）後に大規模種間交雑が開始
2. 更新世の海面変動（氷期の海面低下→河川短縮→繁殖場所の強制的重複）が交雑を促進
3. mtDNAは母系遺伝で有効集団サイズが小さい → 浸透交雑で急速に置換される
4. 一部のmtDNA型が自然選択で有利だった可能性も排除できない

### 生殖隔離のメカニズム（Yamasakiらが議論したもの）

| メカニズム | 説明 | 出典 |
|----------|------|------|
| 産卵場所のミクロ/メソスケール分離 | 河川内での種ごとの産卵場所の違い | Mizuno 1982; Tamada 2000 |
| 同類交配（assortative mating） | 婚姻色に基づく配偶者選択 | Mizuno 1987 |
| 求愛行動の種特異性 | 求愛ディスプレイの違い | Hirashima & Tachihara 2006 |

**ただしこれらのメカニズムは環境撹乱（河川短縮、人為移植）で容易に崩壊する。** Mukai et al. (2012) は人為移植後の種間交雑を報告。

---

## 8. 本プロジェクトへの含意

### SPECIES_CRITERIA.md の仮評価との対応

| 論文の結論 | SPECIES_CRITERIAでの扱い | 整合性 |
|----------|----------------------|--------|
| sp.ORは核DNAで非単系統 | kurodai = sp.OR（Tier 3c） | **一致** |
| sp.BW + sp.BF は弱い支持で単系統 | biwaensis/tyoni = Tier 3a相当（既存記載尊重） | **一致** |
| sp.BB, sp.MO は独立系統 | sp.BB = Tier 2, sp.MO = Tier 2 | **一致** |
| sp.TO は flumineus から分化 | R. telma = Tier 1 | **一致** |
| nagoyae + sp.CO が姉妹群 | nagoyae = Tier 1, mizunoi = Tier 2 | **一致** |

### sp.OR内部の回遊型/陸封型問題に対して

**この論文はsp.OR内部の形態型（橙色型・縞鰭型・宍道湖型・偽橙色型）を区別していない。** sp.ORは全て "amphidromous, small egg" として一括処理。

しかし間接的に重要な情報:

1. **sp.ORから陸封型が分化する際、矮小化が収斂的に起きる**: sp.TO, sp.BF, sp.BW の3種が別系統から独立に同じdwarf morphologyを獲得（L579-584）。sp.OR内部でも陸封化した個体群は矮小化の方向に向かっていると予測できる

2. **amphidromous → lentic の卵サイズ変化は小さい**（L552-553）: sp.OR内の陸封型が卵サイズで回遊型と区別できるかは不確実。ただしMaruyama et al. (2003) が琵琶湖で個体群間変異を報告済み

3. **淡水型は回遊型よりmtDNA浸透を受けにくい**（L484-488）: sp.OR内の陸封型集団が回遊型集団と遺伝的に分化しているとすれば、それは陸封化による生殖隔離の効果であり、既にtou_yoshinobori_complex.mdで発見したsreb2ハプロタイプ完全非共有と整合する

4. **生活史変化は不可逆**（L586-594）: sp.OR内の陸封型は、一度陸封化すると回遊型に戻れない。これは陸封型集団の遺伝的独自性が時間とともに強化される方向に働く

### 論文0（種認定基準）への引用

Yamasaki et al. (2015) は以下の文脈で引用すべき:
- mtDNA浸透交雑の直接的証拠（mtDNAのみの分類が不適切である根拠）
- 核DNA系統樹による種の単系統性の検定（AU test）
- 生活史変化と卵サイズ変化の対応（生態的種分化の文脈）
- sp.ORの非単系統性（kurodai = sp.ORの根拠の一つ）

### 論文2（sp.OR内の回遊型/陸封型）への引用

- sp.ORから止水型が分化するパターンの先例（sp.BF, sp.BW, sp.OM）
- 淡水型のmtDNA浸透耐性 → 生殖隔離の間接的証拠
- 矮小化の収斂 → 形態的識別の手がかり
- 生活史変化の不可逆性 → 陸封型の遺伝的独自性は不可逆的に蓄積される

---

## 9. 補足: Table 1 のsp.ORサンプル一覧

| 標本ID | 河川/採集地 | 地点番号 |
|--------|----------|---------|
| OR-IW081011-2 | Pond / Kitakami R. (Ichinoseki, Iwate) | 2 |
| OR-IW080521-* | Channel / Kitakami R. (Ohshu, Iwate) | 3 |
| OR-FS091026-1* | Otokine R. / Abukuma R. (Tamura, Fukushima) | 5 |
| OR-FS091026-* | Otokine R. / Abukuma R. (Tamura, Fukushima) | 5 |
| OR-NI110816-1* | Seki R. / Seki R. (Joetsu, Niigata) | 6 |
| OR-NI110816-2 | Seki R. / Seki R. (Joetsu, Niigata) | 6 |
| OR-YN120714-5 | Furefuki R. / Fujigawa R. (Koufu, Yamanashi) | 9 |
| OR-HK110724-5 | Irrigation channel / Saigou R. (Fukutsu, Fukuoka) | 32 |
| OR-HK110724-6 | Irrigation channel / Saigou R. (Fukutsu, Fukuoka) | 32 |
| OR-HO120408-1 | Ashabiri R. / Ashabiri R. (Memanbetsu, Hokkaido) | 1 |

**注目点**: 北海道（網走・女満別）からもsp.ORとしてサンプリング。SPECIES_CRITERIAでは北海道産を独立個体群の可能性ありとしているが、Yamasakiらは本土sp.ORに含めている。

---

## 参考文献（論文内で特に重要なもの）

- Katoh M, Nishida M (1994) — 沖縄のbrunneus complex のアロザイム解析。同所的種分化の先例
- Takahashi S, Okazaki T (2002) — 琵琶湖のlentic型sp.BW vs 湖河回遊型sp.OR
- Mukai T et al. (2005) — 小笠原・琉球のmtDNA多型。浸透交雑の先行研究
- Mukai T et al. (2012) — 三重県のため池での人為移植後の種間交雑
- Kano Y et al. (2012) — 滝によるsp.YBの並行進化
- Kondo M et al. (2013) — sp.BBの起源（sp.MOから分化）
- Hirashima K, Tachihara K (2000) — sp.YB, sp.BB の塩分耐性喪失
- Tsunagawa T, Suzuki T, Arai T (2010a) — 縞鰭型の耳石分析（完全淡水定住）
