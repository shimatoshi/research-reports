"""ローカルHTMLファイルからZIMファイルを生成するスクリプト"""
import os
import sys
import sqlite3
import tempfile
import shutil

sys.path.insert(0, '/home/zimmaker')
from packer import ZimPacker

# 対象HTMLファイル
HTML_FILES = [
    ('biology/fish/luciogobius/mimizuhaze_guide.html', 'ミミズハゼ採集ガイド'),
    ('biology/fish/bathygobius/kumohaze_guide.html', 'クモハゼ生態ガイド'),
    ('biology/fish/nijimasu_fishing_guide.html', 'ニジマス釣りガイド'),
    ('biology/fishery/free_seafood_wild_food_guide.html', '漁業権フリー水産物＋野草ガイド'),
    ('biology/intertidal/shellfish_guide.html', '貝の採取・法規制ガイド'),
    ('biology/intertidal/edible_seaweed_guide.html', '食用海藻ガイド'),
    # 既存レポートも含める
    ('biology/intertidal/kanto_rocky_intertidal_guide.html', '関東の磯 生き物総合図鑑'),
    ('biology/intertidal/odawara_hayakawa_guide.html', '小田原～早川 磯採集ガイド'),
    ('biology/fishery/kanto_fishery_guide.html', '関東 水産物・漁業規則 総合ガイド'),
    ('biology/fish/hayakawa_river_guide.html', '早川水系 淡水生物採集ガイド'),
    ('biology/insects-kanto/okuwagata/inba_origin_trace.html', '印旛オオクワガタ伝聞の出典トレース'),
]

FAKE_DOMAIN = 'research-reports.local'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_ZIM = os.path.join(BASE_DIR, 'archives', 'research-reports.zim')

def main():
    os.makedirs(os.path.join(BASE_DIR, 'archives'), exist_ok=True)

    # 一時DBを作成
    tmp_db = tempfile.mktemp(suffix='.db')
    conn = sqlite3.connect(tmp_db)
    c = conn.cursor()
    c.execute('''CREATE TABLE pages (
        url TEXT PRIMARY KEY,
        depth INTEGER,
        status INTEGER,
        filepath TEXT,
        mime TEXT,
        title TEXT,
        parent_url TEXT,
        charset TEXT
    )''')
    c.execute('''CREATE TABLE meta (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')

    # インデックスページを生成
    index_html = _build_index_page()
    index_path = os.path.join(BASE_DIR, 'archives', '_index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)

    # インデックスをDBに登録
    index_url = f'https://{FAKE_DOMAIN}/'
    c.execute('INSERT INTO pages VALUES (?,?,?,?,?,?,?,?)',
              (index_url, 0, 1, index_path, 'text/html',
               '調査レポート集', None, 'utf-8'))

    # 各HTMLファイルをDBに登録
    for rel_path, title in HTML_FILES:
        abs_path = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(abs_path):
            print(f'  ⚠️ スキップ（ファイルなし）: {rel_path}')
            continue
        fake_url = f'https://{FAKE_DOMAIN}/{rel_path}'
        c.execute('INSERT INTO pages VALUES (?,?,?,?,?,?,?,?)',
                  (fake_url, 1, 1, abs_path, 'text/html',
                   title, index_url, 'utf-8'))
        print(f'  ✅ {rel_path} ({title})')

    conn.commit()
    conn.close()

    # ZIMにパック
    packer = ZimPacker(tmp_db, OUTPUT_ZIM, keep_external=True)
    packer.pack()

    # 一時DB削除
    os.unlink(tmp_db)
    os.unlink(index_path)

    # Downloadにコピー
    dl_path = os.path.expanduser('~/storage/downloads/research-reports.zim')
    if os.path.exists(OUTPUT_ZIM):
        shutil.copy2(OUTPUT_ZIM, dl_path)
        size_mb = os.path.getsize(OUTPUT_ZIM) / 1024 / 1024
        print(f'\n📱 コピー完了: {dl_path} ({size_mb:.1f} MB)')


def _build_index_page():
    """目次ページのHTMLを生成"""
    items = ''
    for rel_path, title in HTML_FILES:
        items += f'<a href="{rel_path}" class="card"><span class="name">{title}</span><span class="path">{rel_path}</span></a>\n'

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>調査レポート集</title>
<style>
:root{{--bg:#0f1923;--card:#1a2733;--accent:#4fc3f7;--text:#e0e0e0;--text2:#90a4ae;--border:#2a3a4a}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,'Noto Sans JP',sans-serif;background:var(--bg);color:var(--text);line-height:1.7;font-size:15px;padding:16px}}
h1{{text-align:center;color:#fff;margin:20px 0;font-size:22px}}
.sub{{text-align:center;color:var(--text2);font-size:13px;margin-bottom:24px}}
.grid{{max-width:800px;margin:0 auto;display:flex;flex-direction:column;gap:10px}}
.card{{display:block;background:var(--card);border:1px solid var(--border);border-radius:10px;padding:16px;text-decoration:none;transition:.2s}}
.card:hover{{border-color:var(--accent)}}
.card .name{{display:block;color:var(--accent);font-size:16px;font-weight:bold}}
.card .path{{display:block;color:var(--text2);font-size:12px;margin-top:4px}}
</style>
</head>
<body>
<h1>調査レポート集</h1>
<div class="sub">Research Reports Archive — Offline ZIM Edition</div>
<div class="grid">
{items}
</div>
</body>
</html>'''


if __name__ == '__main__':
    main()
