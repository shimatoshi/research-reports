"""Build offline-db -> ZIM using libzim Python binding (drop-in alternative to pack_to_zim.py
when /home/zimmaker is not available)."""
import os
import sys
from libzim.writer import Creator, Item, StringProvider, FileProvider, Hint, Compression

REPO = "/home/kobayashi-takeru/work/shimatoshi/research-reports"
OFFLINE = os.path.join(REPO, "offline-db")
OUT = os.path.join(REPO, "archives", "research-reports.zim")

MIME_MAP = {
    ".html": "text/html",
    ".webp": "image/webp",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".css": "text/css",
}

import re
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL | re.IGNORECASE)


def extract_title(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as f:
            head = f.read(4096)
        m = TITLE_RE.search(head)
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return fallback


class FileItem(Item):
    def __init__(self, path, abs_path, title, mime):
        super().__init__()
        self._path = path
        self._abs = abs_path
        self._title = title
        self._mime = mime

    def get_path(self):
        return self._path

    def get_title(self):
        return self._title

    def get_mimetype(self):
        return self._mime

    def get_contentprovider(self):
        return FileProvider(self._abs)

    def get_hints(self):
        return {Hint.FRONT_ARTICLE: self._mime == "text/html"}


def main():
    if not os.path.isdir(OFFLINE):
        sys.exit(f"missing offline-db: {OFFLINE}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)

    if os.path.exists(OUT):
        os.unlink(OUT)

    items = []
    for root, _dirs, files in os.walk(OFFLINE):
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in MIME_MAP:
                continue
            abs_path = os.path.join(root, fn)
            rel = os.path.relpath(abs_path, OFFLINE).replace(os.sep, "/")
            mime = MIME_MAP[ext]
            title = extract_title(abs_path, rel) if mime == "text/html" else os.path.basename(rel)
            items.append((rel, abs_path, title, mime))
    items.sort(key=lambda x: x[0])

    main_path = "index.html"
    if not any(p == main_path for p, _, _, _ in items):
        sys.exit("missing top index.html")

    with Creator(OUT).config_indexing(True, "ja").config_compression(Compression.zstd) as creator:
        creator.set_mainpath(main_path)
        creator.add_metadata("Title", "Research Reports — Offline DB")
        creator.add_metadata("Description", "在野研究者のためのオフライン参照データベース")
        creator.add_metadata("Language", "jpn")
        creator.add_metadata("Creator", "research-reports")
        creator.add_metadata("Publisher", "research-reports")
        creator.add_metadata("Name", "research-reports")
        creator.add_metadata("Tags", "biology;fishery;intertidal;history;fight")
        creator.add_metadata("Date", "2026-04-28")

        for rel, abs_path, title, mime in items:
            creator.add_item(FileItem(rel, abs_path, title, mime))

    size_mb = os.path.getsize(OUT) / 1024 / 1024
    print(f"OK: {OUT}  ({size_mb:.1f} MB)  files={len(items)}")


if __name__ == "__main__":
    main()
