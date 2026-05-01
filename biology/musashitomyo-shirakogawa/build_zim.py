#!/usr/bin/env python3
"""
ムサシトミヨ調査レポートを単一 ZIM ファイル化する。
Kiwix リーダー / Kiwix Serve でオフライン閲覧可能。

依存: pip install libzim
"""
import os
from libzim.writer import Creator, Item, FileProvider, StringProvider, Hint

BASE_DIR = "/home/kobayashi-takeru/musashitomyo-survey"
OUT_PATH = "/home/kobayashi-takeru/musashitomyo-survey/musashitomyo-shirakogawa.zim"

# (zim path, local file, mimetype, title, is_main)
FILES = [
    ("index.html", "index.html", "text/html", "ムサシトミヨ調査レポート 白子川源流ピボット", True),
    ("README.md", "README.md", "text/markdown", "README", False),
    ("build_gpx.py", "build_gpx.py", "text/x-python", "build_gpx.py (GPX生成スクリプト)", False),
    ("musashitomyo-shirakogawa.gpx", "musashitomyo-shirakogawa.gpx",
     "application/gpx+xml", "ムサシトミヨ調査用 GPX レイヤー (waypoint 14)", False),
]

METADATA = {
    "Name":        "musashitomyo-shirakogawa",
    "Title":       "ムサシトミヨ調査レポート — 白子川源流ピボット",
    "Description": "AI 横断統合調査による citogenesis 検出と、武蔵野台地ハケ湧水ロジックでの白子川源流候補地特定。OsmAnd 用 GPX レイヤー添付。",
    "LongDescription": (
        "「印旛沼で消滅したムサシトミヨを探す」という出発点から、"
        "Wikipedia 編集履歴遡及により千葉県分布説の citogenesis を検出、"
        "学術一次出典 (池田 1933, 中村 1980, 金澤 2009 等) を整理し、"
        "武蔵野台地ハケ湧水ロジックで白子川源流 (大泉井頭公園) を主候補に特定した調査レポート。"
        "14 waypoint の OsmAnd 互換 GPX レイヤーと生成スクリプトを同梱。"
    ),
    "Language":    "jpn",
    "Creator":     "shimatoshi",
    "Publisher":   "shimatoshi/research-reports",
    "Date":        "2026-05-01",
    "Tags":        "biology;research;ecology;musashitomyo;tokyo;shirakogawa",
    "Source":      "https://github.com/shimatoshi/research-reports/tree/main/biology/musashitomyo-shirakogawa",
    "Scraper":     "musashitomyo-survey/build_zim.py (libzim)",
}


class FileItem(Item):
    def __init__(self, path, title, mimetype, local_path, is_front=False):
        super().__init__()
        self._path = path
        self._title = title
        self._mimetype = mimetype
        self._local = local_path
        self._is_front = is_front

    def get_path(self):     return self._path
    def get_title(self):    return self._title
    def get_mimetype(self): return self._mimetype
    def get_contentprovider(self): return FileProvider(self._local)
    def get_hints(self):
        return {Hint.FRONT_ARTICLE: self._is_front}


def main():
    if os.path.exists(OUT_PATH):
        os.unlink(OUT_PATH)

    with Creator(OUT_PATH).config_indexing(True, "jpn") as c:
        for k, v in METADATA.items():
            c.add_metadata(k, v)

        main_path = None
        for zim_path, local_name, mime, title, is_main in FILES:
            local_path = os.path.join(BASE_DIR, local_name)
            if not os.path.exists(local_path):
                print(f"  ⚠ skip (missing): {local_path}")
                continue
            item = FileItem(zim_path, title, mime, local_path, is_front=is_main)
            c.add_item(item)
            size = os.path.getsize(local_path)
            print(f"  + {zim_path:42s} {size:>7d}b  {mime}")
            if is_main:
                main_path = zim_path

        if main_path:
            c.set_mainpath(main_path)
            print(f"  main: {main_path}")

    sz = os.path.getsize(OUT_PATH)
    print(f"\n✅ Wrote {OUT_PATH} ({sz} bytes / {sz/1024:.1f} KB)")


if __name__ == "__main__":
    main()
