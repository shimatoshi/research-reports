#!/usr/bin/env python3
"""
ムサシトミヨ調査プロジェクト - OsmAnd 用 GPX 生成スクリプト

データソース:
- 池田1933, 中村1980, 金澤2009 (一次出典)
- 第2回・第4回自然環境保全基礎調査 (環境省)
- 千葉県レッドデータブック動物編 2011改訂版
- 白子川散策マップ (白子川流域環境協議会発行)
- nitter.net 経由のSNS情報 (@sugalohas / @kaccekyodo / @little_shotaro 等)
- 練馬区立中里郷土の森 自然観察記録
- Wikipedia 各地点 infobox (座標)
"""
from xml.sax.saxutils import escape
from datetime import datetime, timezone

# 各waypoint: (lat, lon, name, category, color, desc)
# category 凡例:
#   PRIMARY    : 🎯 第一候補地 (現地踏査優先) - 赤
#   HISTORICAL : 📍 一次出典あり過去分布地 - オレンジ
#   PARTNER    : 🤝 連携団体・組織拠点 - 青
#   REFERENCE  : 🔬 比較参考地 (現存生息地・再導入候補) - 紫
#   SURVEY     : 🥾 散策・観察ポイント - 緑

WAYPOINTS = [
    # ===== 🎯 第一候補地 =====
    {
        "lat": 35.745946, "lon": 139.577168,
        "name": "大泉井頭公園 (白子川源流) ★最優先",
        "cat": "PRIMARY", "color": "#FF0000",
        "desc": (
            "【白子川源流の起点・七福橋】\n\n"
            "■ 確定生息種 (一次資料 + SNS):\n"
            "・ホトケドジョウ (絶滅危惧IB類) — 産卵期2-3月、定着繁殖中\n"
            "・ナガエミクリ (水生植物・絶滅危惧)\n"
            "・ミクリ・メダカ・フナ\n"
            "・カワセミ・コサギ・カワウ\n\n"
            "■ 環境条件 (ムサシトミヨ要求条件と一致):\n"
            "・湧水: 河床・護岸から湧出 (大泉地下水瀑布線)\n"
            "・水温: 比較的低温で安定\n"
            "・水草繁茂、流れ緩やか\n"
            "・生活排水流入なし (公園管理)\n\n"
            "■ 保全活動: 「白子川源流・水辺の会」(@sugalohas)\n"
            "毎月第四日曜日13:30〜定例活動 (川そうじ・水質/水位/生き物調査・"
            "アメリカザリガニ駆除・水草間引き)。会員以外も参加可。\n\n"
            "■ 年次イベント: 「白子川源流まつり」毎年10月\n"
            "(2022〜2025連続開催。健康チェック・クイズラリー・展示)\n\n"
            "■ アクセス: 西武池袋線 大泉学園駅 北口徒歩約15分\n"
            "住所: 練馬区東大泉7-34-1\n"
            "公園面積: 約5,700m² (細長い河川沿い公園)"
        ),
    },
    {
        "lat": 35.7558, "lon": 139.5300,
        "name": "落合川 + 南沢湧水群 (東久留米)",
        "cat": "PRIMARY", "color": "#FF0000",
        "desc": (
            "【都内ベストの清流・武蔵野台地北縁】\n\n"
            "■ 既確認魚類:\n"
            "・ホトケドジョウ・シマドジョウ・アブラハヤ・タカハヤ\n"
            "(湧水の礫底に生息する冷水性魚類)\n\n"
            "■ 環境:\n"
            "・南沢湧水群の最上流、年間水温約15℃で安定\n"
            "・国分寺崖線同等のハケ湧水帯\n"
            "・「平成の名水百選」選定地\n\n"
            "■ ムサシトミヨ過去出典: なし (地理ロジックでの候補)\n"
            "■ 既調査の網は薄め。eDNA投入価値あり\n\n"
            "※ 座標は概略 (源流域)。正確には現地で確認"
        ),
    },
    {
        "lat": 35.7028, "lon": 139.4658,
        "name": "真姿の池湧水群 (野川源流)",
        "cat": "PRIMARY", "color": "#FF0000",
        "desc": (
            "【国分寺崖線本流の湧水帯】\n\n"
            "■ 国分寺市東元町、お鷹の道沿い\n"
            "■ 「東京の名湧水57選」「全国名水百選」\n"
            "■ 野川の源流のひとつ (恋ヶ窪湧水と並ぶ)\n"
            "■ 武蔵野台地最大級の湧水ネットワーク\n\n"
            "■ ムサシトミヨ過去出典: なし\n"
            "■ 規模・水質・温度の点で候補上位"
        ),
    },

    # ===== 📍 一次出典あり過去分布地 (調査済み・60年見つかっていない) =====
    {
        "lat": 35.73889, "lon": 139.59750,
        "name": "三宝寺池 (石神井公園)",
        "cat": "HISTORICAL", "color": "#FFA500",
        "desc": (
            "【ムサシトミヨ過去分布地・一次出典あり】\n\n"
            "■ 出典:\n"
            "・池田1933 動物學雑誌45:141-173\n"
            "・中村1963/1980\n"
            "・金澤2009 魚類学雑誌56(2):175\n\n"
            "■ 武蔵野三大湧水池の一つ\n"
            "■ 湧水減退、現在はポンプ補水で水位維持\n"
            "■ 60年以上重点的調査されてきたが現在ムサシトミヨ未確認\n"
            "■ 集団残存の可能性は極めて低い\n"
            "(魚は休眠卵を持たないため井の頭池シャジクモ型復活モデル不可)\n\n"
            "■ 練馬区指定文化財「三宝寺池沼沢植物群落」"
        ),
    },
    {
        "lat": 35.70083, "lon": 139.57417,
        "name": "井の頭池 (井の頭恩賜公園)",
        "cat": "HISTORICAL", "color": "#FFA500",
        "desc": (
            "【ムサシトミヨ過去分布地・一次出典あり】\n\n"
            "■ 出典: 池田1933、中村1980、金澤2009\n"
            "■ 武蔵野三大湧水池\n"
            "■ かいぼり実施実績 (2014, 2017, 2018) — シャジクモ等水生植物復活\n"
            "■ 認定NPO法人 生態工房がかいぼり隊運営\n"
            "■ 重度に魚類調査済み、現在ムサシトミヨ未確認\n\n"
            "※ 注: 三鷹市の井の頭恩賜公園。練馬区の大泉井頭公園とは別物"
        ),
    },
    {
        "lat": 35.714806, "lon": 139.591028,
        "name": "善福寺池 (善福寺公園)",
        "cat": "HISTORICAL", "color": "#FFA500",
        "desc": (
            "【ムサシトミヨ過去主分布地・一次出典あり】\n\n"
            "■ 出典: 中村1980が「主分布地」と明記\n"
            "・池田1933、金澤2009\n"
            "■ 杉並区善福寺3丁目、武蔵野三大湧水池\n"
            "■ 善福寺川の源流\n"
            "■ 湧水減退、ポンプ補水\n"
            "■ 重度に調査済み、現在ムサシトミヨ未確認"
        ),
    },

    # ===== 🔬 比較参考地 =====
    {
        "lat": 36.131750, "lon": 139.396278,
        "name": "熊谷市ムサシトミヨ保護センター",
        "cat": "REFERENCE", "color": "#800080",
        "desc": (
            "【世界唯一の現存ムサシトミヨ生息地】\n\n"
            "■ 元荒川源流域 (熊谷市佐谷田)\n"
            "■ 1991年3月 県指定天然記念物指定\n"
            "■ 1991年11月 埼玉県の魚に指定\n"
            "■ 2011年 熊谷市の魚に指定\n\n"
            "■ 重要な事実:\n"
            "・1963年以降ポンプ揚水で源流水を維持\n"
            "(自然湧水は枯渇済み、人工生命維持装置)\n"
            "・個体数推移: 1986〜2021で2,345〜33,510個体\n"
            "・2002年ピーク (33,510)、その後減少傾向\n\n"
            "■ 連絡先: 熊谷市環境政策 048-536-1547"
        ),
    },
    {
        "lat": 36.244732, "lon": 139.195411,
        "name": "元小山川 (本庄市) — 再導入候補",
        "cat": "REFERENCE", "color": "#800080",
        "desc": (
            "【一次出典のある唯一の非熊谷地点】\n\n"
            "■ 出典: 池田1933、金澤2009\n"
            "■ 金澤(2009)が再導入計画の対象として明記\n"
            "■ 埼玉県本庄市\n"
            "■ 学術的に最も裏付けの強い「印旛沼」以外の候補\n\n"
            "■ 座標は河川全体の代表点。源流踏査時に絞り込み要"
        ),
    },

    # ===== 🤝 連携団体 =====
    {
        "lat": 35.7659611, "lon": 139.6073472,
        "name": "練馬区立中里郷土の森緑地",
        "cat": "PARTNER", "color": "#0066FF",
        "desc": (
            "【自然解説員常駐の体験型学習拠点】\n\n"
            "■ 練馬区大泉町1丁目、2017年3月開園、面積2,500m²\n"
            "■ 100年以上前の屋敷跡地\n"
            "■ 30種超の野鳥、約300種の昆虫類確認\n\n"
            "■ 定期調査:\n"
            "・週1回 園内調査\n"
            "・月1回 周辺緑地調査\n"
            "・年1回 白子川・石神井川の魚類調査 (10月)\n\n"
            "■ 主催イベント:\n"
            "「親子で白子川大調査!」毎年10月、源流部に入って生き物採集\n"
            "2021年10/9実績: アブラハヤ・ホトケドジョウ・カワリヌマエビ・"
            "ヒキガエル・アオダイショウ・クサガメ確認\n"
            "(過去の白子川調査でカワヨシノボリ=国内外来種を発見した記録あり)\n\n"
            "■ 公式: https://www.ces-net.jp/nakazato/"
        ),
    },
    {
        "lat": 35.7355, "lon": 139.6519,
        "name": "練馬区役所 (環境部みどり推進課)",
        "cat": "PARTNER", "color": "#0066FF",
        "desc": (
            "【練馬区の自然環境関連窓口】\n\n"
            "■ 環境部みどり推進課\n"
            "■ TEL: 03-5984-2418 (平日8:30-17:15)\n"
            "■ 住所: 練馬区豊玉北6-12-1\n\n"
            "■ 問い合わせ事項候補:\n"
            "・練馬区自然環境調査の魚類章PDF所在\n"
            "・白子川流域の魚類調査結果データ\n"
            "・(公財)練馬区環境まちづくり公社の連絡先"
        ),
    },

    # ===== 🥾 散策・観察ポイント (白子川上流域の橋名) =====
    {
        "lat": 35.7460, "lon": 139.5772,
        "name": "七福橋 (白子川起点)",
        "cat": "SURVEY", "color": "#008000",
        "desc": "白子川の上流端、起点 (練馬区東大泉7丁目34番)。大泉井頭公園内。"
    },
    {
        "lat": 35.7475, "lon": 139.5825,
        "name": "学園橋",
        "cat": "SURVEY", "color": "#008000",
        "desc": "白子川上流域、東大泉学園通り近辺。観察ポイント。"
    },
    {
        "lat": 35.7485, "lon": 139.5860,
        "name": "外山橋〜水道橋 (we love 白子川の会 活動エリア)",
        "cat": "SURVEY", "color": "#008000",
        "desc": (
            "白子川中流。「we love 白子川の会」(@weloveshirako) 活動拠点。\n"
            "毎月第三日曜日10時〜活動 (手作り堰維持等)。\n"
            "上流の「白子川源流・水辺の会」と二層体制で流域を保全。"
        ),
    },
    {
        "lat": 35.7495, "lon": 139.5895,
        "name": "比丘尼橋上流調節池 (ぴくに公園)",
        "cat": "SURVEY", "color": "#008000",
        "desc": "白子川上流、調節池機能を持つ。水位変動あり。"
    },
]

def build_gpx(waypoints, out_path):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    parts = []
    parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    parts.append(
        '<gpx version="1.1" creator="MusashiTomyoSurvey" '
        'xmlns="http://www.topografix.com/GPX/1/1" '
        'xmlns:osmand="https://osmand.net" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://www.topografix.com/GPX/1/1 '
        'http://www.topografix.com/GPX/1/1/gpx.xsd">'
    )
    parts.append('<metadata>')
    parts.append('<name>ムサシトミヨ調査プロジェクト 白子川中心</name>')
    parts.append(f'<time>{now}</time>')
    parts.append(
        '<desc>白子川源流(大泉井頭公園)を主候補とした'
        'ムサシトミヨ再発見調査用レイヤー。'
        '池田1933/中村1980/金澤2009/環境省自然環境保全基礎調査/'
        'nitter経由SNS情報を統合。</desc>'
    )
    parts.append('</metadata>')

    cat_label = {
        "PRIMARY":    "★第一候補",
        "HISTORICAL": "歴史地点",
        "PARTNER":    "連携先",
        "REFERENCE":  "参考",
        "SURVEY":     "観察点",
    }

    for w in waypoints:
        parts.append(f'<wpt lat="{w["lat"]}" lon="{w["lon"]}">')
        parts.append(f'  <name>{escape(w["name"])}</name>')
        parts.append(f'  <desc>{escape(w["desc"])}</desc>')
        parts.append(f'  <type>{cat_label.get(w["cat"], w["cat"])}</type>')
        parts.append('  <extensions>')
        parts.append(f'    <osmand:color>{w["color"]}</osmand:color>')
        parts.append('    <osmand:icon>special_star</osmand:icon>'
                     if w["cat"] == "PRIMARY"
                     else '    <osmand:icon>special_marker</osmand:icon>')
        parts.append('    <osmand:background>circle</osmand:background>')
        parts.append('  </extensions>')
        parts.append('</wpt>')

    parts.append('</gpx>')
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    return len(waypoints)

if __name__ == "__main__":
    out = "/home/kobayashi-takeru/musashitomyo-survey/musashitomyo-shirakogawa.gpx"
    n = build_gpx(WAYPOINTS, out)
    print(f"Generated {n} waypoints -> {out}")
