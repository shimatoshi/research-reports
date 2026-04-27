"""offline-db/ 配下のHTML+画像をZIM化するスクリプト"""
import os
import re
import sys
import sqlite3
import tempfile
import shutil

sys.path.insert(0, '/home/zimmaker')
from packer import ZimPacker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OFFLINE_DIR = os.path.join(BASE_DIR, 'offline-db')
OUTPUT_ZIM = os.path.join(BASE_DIR, 'archives', 'research-reports.zim')
FAKE_DOMAIN = 'research-reports.local'
TOP_INDEX = 'index.html'  # offline-db/index.html がトップ目次

# ZIMに含める拡張子 → MIME
MIME_MAP = {
    '.html': 'text/html',
    '.webp': 'image/webp',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.css': 'text/css',
}

TITLE_RE = re.compile(r'<title>(.*?)</title>', re.DOTALL | re.IGNORECASE)


def collect_files():
    """offline-db/配下を再帰スキャン。(rel_path, abs_path, mime) のリストを返す"""
    items = []
    for root, _dirs, files in os.walk(OFFLINE_DIR):
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in MIME_MAP:
                continue
            abs_path = os.path.join(root, fn)
            rel_path = os.path.relpath(abs_path, OFFLINE_DIR).replace(os.sep, '/')
            items.append((rel_path, abs_path, MIME_MAP[ext]))
    items.sort(key=lambda x: x[0])
    return items


def extract_title(html_path, fallback):
    try:
        with open(html_path, encoding='utf-8') as f:
            head = f.read(4096)
        m = TITLE_RE.search(head)
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return fallback


def main():
    if not os.path.isdir(OFFLINE_DIR):
        print(f'❌ offline-db/ が見つかりません: {OFFLINE_DIR}')
        sys.exit(1)

    os.makedirs(os.path.join(BASE_DIR, 'archives'), exist_ok=True)

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
    c.execute('CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)')

    items = collect_files()
    top_url = f'https://{FAKE_DOMAIN}/'
    top_path = os.path.join(OFFLINE_DIR, TOP_INDEX)

    if not os.path.exists(top_path):
        print(f'❌ トップ index.html が見つかりません: {top_path}')
        sys.exit(1)

    # トップページ (ZIMルート / にマッピング)
    top_title = extract_title(top_path, 'Research Reports Offline DB')
    c.execute('INSERT INTO pages VALUES (?,?,?,?,?,?,?,?)',
              (top_url, 0, 1, top_path, 'text/html', top_title, None, 'utf-8'))

    # 各ファイル
    for rel_path, abs_path, mime in items:
        url = f'https://{FAKE_DOMAIN}/{rel_path}'
        is_html = mime == 'text/html'
        title = extract_title(abs_path, rel_path) if is_html else os.path.basename(rel_path)
        charset = 'utf-8' if mime.startswith('text/') else None
        c.execute('INSERT INTO pages VALUES (?,?,?,?,?,?,?,?)',
                  (url, 1, 1, abs_path, mime, title, top_url, charset))

    conn.commit()
    print(f'  📦 {len(items)} ファイル登録 + ルート目次')
    conn.close()

    packer = ZimPacker(tmp_db, OUTPUT_ZIM, keep_external=True)
    packer.pack()

    os.unlink(tmp_db)

    if os.path.exists(OUTPUT_ZIM):
        size_mb = os.path.getsize(OUTPUT_ZIM) / 1024 / 1024
        print(f'\n✅ ZIM生成完了: {OUTPUT_ZIM} ({size_mb:.1f} MB)')

        # Termux等のDownloadフォルダにあればコピー
        dl_path = os.path.expanduser('~/storage/downloads/research-reports.zim')
        if os.path.isdir(os.path.dirname(dl_path)):
            try:
                shutil.copy2(OUTPUT_ZIM, dl_path)
                print(f'📱 コピー: {dl_path}')
            except OSError:
                pass


if __name__ == '__main__':
    main()
