# KURENAI（京大機関リポジトリ）からのPDFダウンロード

KURENAIはDSpace 7ベースのSPAで、フロントエンドはAngular。curlでbitstream URLを叩いてもHTMLが返ってくる。
しかし裏のREST APIは認証不要でPDFを直接返す。

## 手順

### 1. ハンドルからアイテムUUIDを取得

```bash
curl -s "https://repository.kulib.kyoto-u.ac.jp/server/api/discover/search/objects?query=handle:2433/198127" \
  -H "Accept: application/json" | python3 -m json.tool
```

レスポンスから `_embedded.searchResult._embedded.objects[0]._embedded.indexableObject.uuid` を取る。

### 2. バンドル一覧を取得

```bash
curl -s "https://repository.kulib.kyoto-u.ac.jp/server/api/core/items/{item-uuid}/bundles" \
  -H "Accept: application/json"
```

`name: "ORIGINAL"` のバンドルUUIDを探す（PDFが入っている）。

### 3. ビットストリーム情報を取得

```bash
curl -s "https://repository.kulib.kyoto-u.ac.jp/server/api/core/bundles/{bundle-uuid}/bitstreams" \
  -H "Accept: application/json"
```

PDFのファイル名、サイズ、ビットストリームUUIDが返る。

### 4. PDFダウンロード

```bash
curl -s -L -H "Accept: application/pdf" \
  -o output.pdf \
  "https://repository.kulib.kyoto-u.ac.jp/server/api/core/bitstreams/{bitstream-uuid}/content"
```

## ワンライナー（ハンドルからPDFまで）

```bash
HANDLE="2433/198127"
BASE="https://repository.kulib.kyoto-u.ac.jp/server/api"

# アイテムUUID
ITEM_UUID=$(curl -s "$BASE/discover/search/objects?query=handle:$HANDLE" \
  -H "Accept: application/json" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['_embedded']['searchResult']['_embedded']['objects'][0]['_embedded']['indexableObject']['uuid'])")

# ORIGINALバンドルUUID
BUNDLE_UUID=$(curl -s "$BASE/core/items/$ITEM_UUID/bundles" \
  -H "Accept: application/json" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print([b['uuid'] for b in d['_embedded']['bundles'] if b['name']=='ORIGINAL'][0])")

# ビットストリームUUID + ファイル名
read BS_UUID BS_NAME <<< $(curl -s "$BASE/core/bundles/$BUNDLE_UUID/bitstreams" \
  -H "Accept: application/json" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); b=d['_embedded']['bitstreams'][0]; print(b['uuid'], b['name'])")

# ダウンロード
curl -s -L -H "Accept: application/pdf" -o "$BS_NAME" "$BASE/core/bitstreams/$BS_UUID/content"
echo "Downloaded: $BS_NAME"
```

## 適用範囲

- **KURENAI（京大）** — 確認済み、上記手順で動作する
- **他のDSpace 7リポジトリ** — 同じAPIパターンのはず（UTokyo Repository等）。ベースURLを変えれば同様に使える可能性が高い
- **DSpace 5/6** — REST APIの構造が異なる。別途調査が必要

## 論文の探し方（CLIで完結する部分）

1. DOI or タイトルでWebSearchして論文を特定
2. PubMedで「Free article」フラグを確認 → 機関リポジトリへのリンクがある
3. 著者の個人サイト・ResearchGateも並行して探す
4. リポジトリのハンドルが判明したら上記手順でダウンロード

## CLIで取れないケース

- JS必須SPAのフロントエンド（← 今回のようにAPI直叩きで回避可能な場合あり）
- ログイン必須（ResearchGateのPDFダウンロード等）
- Cloudflare bot対策が厳しいサイト
