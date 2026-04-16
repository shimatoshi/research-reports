#!/usr/bin/env python3
"""S-Net (サイエンスミュージアムネット) list scraper for Rhinogobius."""
import os, re, sys, json, time, urllib.request, gzip

BASE = "https://science-net.kahaku.go.jp"
LIST_URL = BASE + "/search/list"
DETAIL_URL = BASE + "/search/detail"

OUT_DIR = os.environ.get("SNET_DIR", os.path.expanduser("/tmp/snet_out"))
LIST_JSONL = os.path.join(OUT_DIR, "list.jsonl")
DETAIL_JSONL = os.path.join(OUT_DIR, "details.jsonl")
DETAIL_HTML_DIR = os.path.join(OUT_DIR, "details_html")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(DETAIL_HTML_DIR, exist_ok=True)

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ja,en;q=0.9",
        "Referer": "https://science-net.kahaku.go.jp/search/",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            d = gzip.decompress(d)
        return d.decode("utf-8", errors="replace")

def build_list_url(pn=1, dispnum=500, field="c2_f", value="Rhinogobius"):
    return (f"{LIST_URL}?secIdx=0&cls=top&pn={pn}&chkCls=collect11"
            f"&c1_f=&{field}={urllib.parse.quote(value)}&c2_a=1&c2_l=2"
            f"&dispnum={dispnum}&sort=&order=0")

import urllib.parse

ROW_RE = re.compile(
    r'<tr[^>]*class="[^"]*result-row[^"]*"[^>]*>(.*?)</tr>'
    , re.DOTALL)

# Fallback: find detail link + adjacent text to extract pkey + species
# Every row has <a href="detail?cls=collect11&pkey=NNN">...</a>
PKEY_RE = re.compile(r'detail\?cls=collect11&(?:amp;)?pkey=(\d+)')

def parse_list(html):
    """Extract rows. For S-Net the list table structure is tabular with cells per row."""
    rows = []
    # Try to find each tr containing a detail link
    for m in re.finditer(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL):
        cell = m.group(1)
        pkey_m = PKEY_RE.search(cell)
        if not pkey_m: continue
        pkey = pkey_m.group(1)
        # Extract text cells
        tds = re.findall(r'<td[^>]*>(.*?)</td>', cell, re.DOTALL)
        tds_text = [re.sub(r'<[^>]+>', ' ', t).strip() for t in tds]
        tds_text = [re.sub(r'\s+', ' ', t) for t in tds_text]
        rows.append({"pkey": pkey, "cells": tds_text})
    return rows

def scrape_list(max_pages=100, dispnum=500):
    if os.path.exists(LIST_JSONL):
        os.remove(LIST_JSONL)
    total = None
    written = 0
    for pn in range(1, max_pages + 1):
        url = build_list_url(pn=pn, dispnum=dispnum)
        try:
            h = fetch(url)
        except Exception as e:
            print(f"  pn={pn} err: {e}", file=sys.stderr)
            time.sleep(5)
            continue
        if total is None:
            m = re.search(r'([0-9,]+)件中', h)
            if m:
                total = int(m.group(1).replace(",", ""))
                print(f"total hits: {total}", file=sys.stderr)
        rows = parse_list(h)
        if not rows:
            print(f"  pn={pn}: 0 rows — stop", file=sys.stderr)
            break
        with open(LIST_JSONL, "a", encoding="utf-8") as f:
            for r in rows:
                r["pn"] = pn
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        written += len(rows)
        print(f"  pn={pn}: rows={len(rows)} total={written}/{total}", file=sys.stderr)
        max_pn_visible = max({int(p) for p in re.findall(r'pn=(\d+)', h)} or {pn})
        if pn >= max_pn_visible:
            break
        time.sleep(0.4)
    return written

def scrape_detail(pkey):
    url = f"{DETAIL_URL}?cls=collect11&pkey={pkey}"
    cache = os.path.join(DETAIL_HTML_DIR, f"{pkey}.html")
    if os.path.exists(cache):
        return open(cache).read()
    h = fetch(url)
    with open(cache, "w") as f: f.write(h)
    return h

def parse_detail(h, pkey):
    pairs = {}
    for m in re.finditer(r'<th[^>]*>(.+?)</th>\s*<td[^>]*>(.+?)</td>', h, re.DOTALL):
        k = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', m.group(1))).strip()
        v = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', m.group(2))).strip()
        if k and (k not in pairs or len(v) > len(pairs[k])):
            pairs[k] = v
    imgs = []
    for m in re.finditer(r'/rest/media/[A-Z][^"\'\s]*pkey=(\d+)', h):
        imgs.append(BASE + m.group(0))
    return {"pkey": pkey, "fields": pairs, "images": list(dict.fromkeys(imgs))}

def fetch_all_details():
    pkeys = set()
    for line in open(LIST_JSONL):
        pkeys.add(json.loads(line)["pkey"])
    already = set()
    if os.path.exists(DETAIL_JSONL):
        for line in open(DETAIL_JSONL):
            already.add(json.loads(line)["pkey"])
    todo = sorted(pkeys - already, key=int)
    print(f"details: have {len(already)}, need {len(todo)}", file=sys.stderr)
    for i, pkey in enumerate(todo):
        try:
            h = scrape_detail(pkey)
            d = parse_detail(h, pkey)
            with open(DETAIL_JSONL, "a", encoding="utf-8") as f:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"  {pkey}: {e}", file=sys.stderr)
        if (i+1) % 50 == 0:
            print(f"  details: {i+1}/{len(todo)}", file=sys.stderr)
        time.sleep(0.2)

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "list"
    if mode in ("all", "list"):
        scrape_list(max_pages=200)
    if mode in ("all", "details"):
        fetch_all_details()
    print("=== DONE ===", file=sys.stderr)
    if os.path.exists(LIST_JSONL):
        print(f"list:    {sum(1 for _ in open(LIST_JSONL))}", file=sys.stderr)
    if os.path.exists(DETAIL_JSONL):
        print(f"details: {sum(1 for _ in open(DETAIL_JSONL))}", file=sys.stderr)

if __name__ == "__main__":
    main()
