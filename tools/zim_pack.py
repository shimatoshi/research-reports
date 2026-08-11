#!/usr/bin/env python3
"""Single HTML -> ZIM using the official libzim Python bindings.

Usage:
  python3 tools/zim_pack.py input.html output.zim [--title "Title"] [--lang jpn]

The previous implementation wrote the ZIM binary format by hand. This version
uses libzim so archives are produced by the reference ZIM implementation.
"""

import argparse
import base64
import os
import re
from datetime import date
from pathlib import Path

from libzim.writer import Creator, Item, StringProvider, Hint

# zimcheck requires a mandatory Illustration_48x48@1 metadata item + favicon.
# Embedded here (instead of a separate binary asset) so the packer stays a
# single self-contained file. 48x48 PNG, "RR" monogram on white/blue.
FAVICON_48PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAABLklEQVR4nO3YMUsCYRzH8d+VroEg"
    "JBIKORxGgVOI0O6ko2BBtLb0BqSpQV+A0JhgQ7g6KDTpGxB0cNBBBGkIjiAkuOzxBfhcPDxyz58H"
    "/p/xN92Xew7uzklVXwQsdkB9AfviAGrWB0Rk4+L11vR1KElft3Y26+8AB1DjAGocQI0DqHEANQ6g"
    "Jn0blXHv2shl4hAC+P7x8XhziXz2OHA3RTkgGjnEW60IAJguPTw0h+jXS4G7KVpHyD2J4cNbK+9h"
    "0goYjFconCWU9zApHyH/d4PKUw/+RmC++sJ7o/zvborWM/DcnaAzmOG+dBG4m6J1hK7OkxjNP5X3"
    "MGkFnCaPMF16+BNCaQ+TI/u1yH8lDOIAahxAjQOocQA1DqDGAdQ4gJr0e8Am1t8BDqBmfcAWFHtv"
    "Abe7az8AAAAASUVORK5CYII="
)


def extract_title(html: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    if not m:
        return "Untitled"
    return re.sub(r"\s+", " ", m.group(1)).strip()


def slugify(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._").lower()
    return value or "research-report"


class HtmlItem(Item):
    def __init__(self, html: str, title: str):
        super().__init__()
        self._html = html
        self._title = title

    def get_path(self):
        return "index.html"

    def get_title(self):
        return self._title

    def get_mimetype(self):
        return "text/html; charset=utf-8"

    def get_contentprovider(self):
        return StringProvider(self._html)

    def get_hints(self):
        return {Hint.FRONT_ARTICLE: True}


def main():
    p = argparse.ArgumentParser(description="Single HTML to ZIM packer using libzim")
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--title")
    p.add_argument("--lang", default="jpn", help="ISO 639-3 language code (default: jpn)")
    p.add_argument("--date", default=None)
    p.add_argument("--name", default=None)
    p.add_argument("--creator", default="shimatoshi")
    p.add_argument("--publisher", default="shimatoshi/research-reports")
    p.add_argument("--description", default=None)
    args = p.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    html = input_path.read_text(encoding="utf-8")
    title = args.title or extract_title(html)
    name = args.name or slugify(output_path.stem)
    zim_date = args.date or date.today().isoformat()
    description = args.description or title

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    metadata = {
        "Name": name,
        "Title": title,
        "Description": description,
        "Language": args.lang,
        "Creator": args.creator,
        "Publisher": args.publisher,
        "Date": zim_date,
        # config_indexing(True, ...) below embeds a real Xapian fulltext
        # index, so advertise it truthfully (kiwi-engine's cross-book search
        # otherwise excludes books whose Tags disagree with the index that's
        # actually present).
        "Tags": "research;report;_ftindex:yes",
        "Scraper": "shimatoshi/research-reports CI (libzim)",
    }

    favicon = base64.b64decode(FAVICON_48PNG_B64)

    with Creator(str(output_path)).config_indexing(True, args.lang) as creator:
        for key, value in metadata.items():
            creator.add_metadata(key, value)
        creator.add_illustration(48, favicon)
        creator.add_item(HtmlItem(html, title))
        creator.set_mainpath("index.html")

    print(f"Packed {input_path} -> {output_path} ({output_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
