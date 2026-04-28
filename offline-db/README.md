# offline-db/

ネット遮断環境でも参照できる調査レポート (HTML) を集約したディレクトリ。

エントリーポイント: [`index.html`](index.html)

## 構成

- `kanto-rocky-shore/` — 関東の磯岩礁生態系 総合 (multi-page, 7章+画像)
- `crustacea-freshwater-brackish/` — 淡水・汽水産甲殻類 総合 (multi-page, 7章+画像)
- `fish/gobies-overview/` — 日本のハゼ類 総合 (multi-page, 7章+画像)
- `fish/`, `fishery/`, `intertidal/`, `insects-kanto/` — 単発HTMLガイド/レポート

multi-page型レポートは MD原稿・WebP画像も同ディレクトリに同梱。HTMLビューアでローカルにそのまま開ける。

## ZIM配信

メインマシン (zimmaker導入済) では:

```bash
python3 pack_to_zim.py
```

zimmaker未導入のマシンでは libzim Python binding で代替:

```bash
pip install --user libzim
python3 build_zim_libzim.py
```

どちらも `archives/research-reports.zim` を生成。Kiwix等で開くと `index.html` が目次として展開される。

## クロス参照ポリシー

レポート間の関連リンクは原則 `offline-db/` 内で完結させる。例外として、研究データセット (例: `biology/fish/rhinogobius/` の個体ベースDB) は元の場所に残るため、HTMLからは `../../biology/...` として参照する。
