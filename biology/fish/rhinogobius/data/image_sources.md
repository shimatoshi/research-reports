# sp.OR群 画像収集計画

作成日: 2026-04-10

## 目的

インターネット上の「トウヨシノボリ」「クロダハゼ」「オウミヨシノボリ」「カズサヨシノボリ」の写真を収集し、形態分類のふるいにかけて精査する。tyoni/shimahire、telma、biwaensisを除外し、sp.OR/kurodai/sp.KZ/sp.OMのみを残して論文と突き合わせる。

## 鑑別キー（写真から判定可能な形質）

```
Step 1: 第一背鰭は伸長するか？
  → しない（将棋駒型）→ 陸封型候補 → Step 2
  → する（烏帽子型）→ 回遊型sp.OR候補 → Step 3

Step 2: 陸封型の鑑別
  → 第二背鰭・尾鰭に縞模様 + 瀬戸内海沿岸産 → tyoni（除外）
  → 第一背鰭に縦長暗色斑の列 + 東海地方産 → telma（除外）
  → 琵琶湖産で矮小 → biwaensis（除外）
  → 上記いずれでもない → 陸封型sp.OR候補（残す）

Step 3: 回遊型の地域判定
  → 関東平野 → kurodai名義で呼ばれている可能性大（= sp.OR）
  → 房総半島 → sp.KZ候補
  → 琵琶湖周辺 → sp.OM候補
  → その他本州・九州 → sp.OR
```

## 収集済みソース

### Tier 1: 構造化データ

| ソース | 件数 | 位置情報 | 状態 |
|--------|------|---------|------|
| iNaturalist (R. kurodai taxon 1078893) | 22件 | あり（一部非公開） | API制限あり、2件のみ取得 |

### Tier 2: ブログ・個人サイト（位置情報あり）

| ソース | 地域 | 種 | URL | 状態 |
|--------|------|-----|-----|------|
| 関東の魚を追って: カズサヨシノボリ | 千葉・房総丘陵 | sp.KZ | https://gyottu2gou.hatenablog.com/entry/2018/04/07/154503 | 取得済み |
| 関東の魚を追って: クロダハゼ@東京 | 東京 | kurodai | https://gyottu2gou.hatenablog.com/entry/2018/09/25/000226 | 取得済み |
| 関東の魚を追って: クロダハゼ@神奈川 | 神奈川・水路 | kurodai | https://gyottu2gou.hatenablog.com/entry/2022/07/08/201906 | 未取得 |
| rhinogobius.jp: クロダハゼ@埼玉 | 埼玉南部 | kurodai | https://rhinogobius.jp/collection/stm01/ | JSレンダリング、手動要 |
| rhinogobius.jp: クロダハゼ@栃木 | 栃木南部 | kurodai | https://rhinogobius.jp/collection/tochigi_kurodai01/ | JSレンダリング、手動要 |
| 海を歩くゲンゴロウ | 関東 | kurodai | https://cybister20.exblog.jp/26696692/ | 未取得 |
| 鮒次郎: 多摩川水系 | 東京・多摩川 | kurodai/sp.OR | https://aiamuhuna.hatenablog.com/entry/14534331 | 未取得 |
| 但馬情報特急 | 兵庫・円山川 | sp.OR | https://www.tajima.or.jp/nature/169574/ | 未取得 |
| 水中すきま: オウミヨシノボリ | 琵琶湖・広島湾 | sp.OM | https://suityu-sukima.sakura.ne.jp/kasen/oumiyosinobori.html | 取得済み |
| 井の頭公園の生き物たち | 東京・井の頭 | kurodai | https://www.bun-shin.co.jp/ikimono28/ | 未取得 |
| WEB魚図鑑: クロダハゼ | 不明 | kurodai | https://zukan.com/fish/leaf172810 | 未取得 |

### Tier 3: 参考資料（図鑑系）

| ソース | 内容 | URL |
|--------|------|-----|
| rhinogobius.jp: クロダハゼ図鑑 | 形態写真・分布情報 | https://rhinogobius.jp/picturebook/kurodai/ |
| rhinogobius.jp: トウヨシノボリ図鑑 | 形態写真・分布情報 | https://rhinogobius.jp/picturebook/spOR/ |
| rhinogobius.jp: カズサヨシノボリ図鑑 | 形態写真・分布情報 | https://rhinogobius.jp/picturebook/spKZ/ |
| 日淡会: トウヨシノボリの混迷 | 形態型の比較・分類議論 | https://tansuigyo.net/a/link7-11a.html |
| 長野県水産試験場 | 諏訪湖のsp.OR | https://www.pref.nagano.lg.jp/suisan/joho/sakanatachi/toyoshinobori.html |
| 大阪府立環境研: シマヒレ | tyoni鑑別の参考 | https://www.knsk-osaka.jp/zukan/ |

### Tier 4: 公的DB

| ソース | 内容 | URL |
|--------|------|-----|
| 河川水辺の国勢調査 | 全国河川の魚類調査データ | https://www.nilim.go.jp/lab/fbg/ksnkankyo/mizukokuweb/ |
| 琵琶湖生物多様性画像DB | 琵琶湖の生物写真 | https://www.lberi.jp/iframe_dir/ |
| 琵琶湖生物標本DB (NIES) | 標本写真+採集地 | https://www.nies.go.jp/biwako_specimens/index.html |
| 侵入生物DB (NIES) | R. kurodaiの分布情報 | https://www.nies.go.jp/biodiversity/invasive/DB/detail/50930e.html |

## 収集済みデータ要約

### sp.KZ（カズサヨシノボリ）— 千葉・房総丘陵
- 泥底の渓流で採集。石をひっくり返して網で捕獲
- 全体的に褐色。一部個体に頬の赤い斑点あり
- 著者: 「カズサヨシノボリの定義に合わない」赤斑個体がいる → 分類の曖昧さを認識
- 「カズサとオウミは将来統合されるかもしれない」との見解

### kurodai（クロダハゼ）— 東京
- 公園池の排水が流入する地点付近でのみ採集 → 池由来の個体群の可能性
- 雌雄の写真あり。性的二型を記録
- 緩流域の抽水植物帯に生息

### sp.OM（オウミヨシノボリ）— 琵琶湖・広島湾
- 琵琶湖の支流と広島湾流入河川に分布
- ビワヨシノボリとの鑑別: 雄の第一背鰭が伸長、吻が長い、頬に赤い斑点、体が大きい
- 繁殖期（5-7月）は浅瀬に出現
- 広島湾流入河川の個体は頬の斑点が顕著

## TODO

- [ ] 未取得のTier 2ブログを順次取得
- [ ] rhinogobius.jpは手動でブラウザからコピー → clipboard経由で取得
- [ ] 河川水辺の国勢調査データのダウンロード可否確認
- [ ] 琵琶湖DBの画像検索
- [ ] 収集画像の形態分類（鑑別キー適用）
- [ ] 位置情報つき個体の地図プロット
