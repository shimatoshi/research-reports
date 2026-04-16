#!/usr/bin/env python3
"""
Fishpix (国立科学博物館) 魚類写真資料データベース scraper.
Rhinogobius属の3160件を取得して採集地・採集日・採集者・画像を収集。

Encoding: Shift_JIS.
"""
import os, re, sys, json, time, urllib.request, urllib.parse

BASE = "https://fishpix.kahaku.go.jp/fishimage"
OUT_DIR = os.environ.get("FISHPIX_DIR", os.path.expanduser("~/fishpix_out"))
IMG_DIR = os.path.join(OUT_DIR, "images")
LIST_JSONL = os.path.join(OUT_DIR, "list.jsonl")
DETAIL_JSONL = os.path.join(OUT_DIR, "details.jsonl")
os.makedirs(IMG_DIR, exist_ok=True)

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def fetch_sjis(url, timeout=30):
    return fetch(url, timeout).decode("shift_jis", errors="replace")

SEARCH_PARAMS = "JPN_FAMILY=&FAMILY=&JPN_NAME=&SPECIES=Rhinogobius&LOCALITY=&FISH_Y=&FISH_M=&FISH_D=&PERSON=&PHOTO_ID=&JPN_FAMILY_OPT=1&FAMILY_OPT=1&JPN_NAME_OPT=1&SPECIES_OPT=1&LOCALITY_OPT=1&PERSON_OPT=1&PHOTO_ID_OPT=1"

ITEM_RE = re.compile(
    r'<img src="\.\./photos/(NR\d+)/(\d+)AI\.jpg"[^>]*>.*?'
    r'<span class="result">([^<]+)</span>.*?'
    r'<span class="resultHelvetica">([^<]+)</span>.*?'
    r'<a href="(detail\?START=(\d+)[^"]+)">KPM-NR\s*(\d+)</a>',
    re.DOTALL)

def parse_list(html):
    items = []
    for m in ITEM_RE.finditer(html):
        items.append({
            "nr_dir":  m.group(1),
            "photo_id_num": m.group(2),
            "ja": m.group(3).strip(),
            "lat": m.group(4).strip(),
            "detail_url_rel": m.group(5).replace("&amp;", "&"),
            "start": int(m.group(6)),
            "kpm_nr_id": f"KPM-NR {m.group(7)}",
            "thumb_url": f"https://fishpix.kahaku.go.jp/photos/{m.group(1)}/{m.group(2)}AI.jpg",
            "full_url":  f"https://fishpix.kahaku.go.jp/photos/{m.group(1)}/{m.group(2)}AF.jpg",
        })
    return items

DETAIL_FIELD_RE = re.compile(r'<span class="caption">([^：]+)：([^<]*)</span>')

def parse_detail(html):
    """Extract 撮影場所, 撮影日, 撮影者, 水深, 備考 + other fields."""
    data = {"all_images": []}
    # Pull the metadata block after the image
    for m in DETAIL_FIELD_RE.finditer(html):
        k = m.group(1).strip()
        v = m.group(2).strip()
        data[k] = v
    # All image URLs on the page
    for m in re.finditer(r'<img[^>]+src="\.\./photos/(NR\d+)/(\d+)A[A-Z]\.jpg"', html):
        data["all_images"].append(f"https://fishpix.kahaku.go.jp/photos/{m.group(1)}/{m.group(2)}{m.group(0).split('/')[-1].split('.')[0][-2:]}.jpg")
    # species/Japanese name fallback
    sj = re.search(r'<span class="caption">([^<]+) \((ハゼ科|[^<]+科)\)</span>', html)
    if sj:
        data["species_ja_full"] = sj.group(1).strip()
        data["family_ja"] = sj.group(2).strip()
    slat = re.search(r'<span class="caption">(Rhinogobius[^<]*)\[[^<]+\]</span>', html)
    if slat:
        data["species_lat_full"] = slat.group(1).strip()
    return data

def scrape_lists():
    if os.path.exists(LIST_JSONL):
        os.remove(LIST_JSONL)
    start = 1
    total = None
    total_collected = 0
    while True:
        url = f"{BASE}/search?START={start}&{SEARCH_PARAMS}"
        try:
            html = fetch_sjis(url, timeout=30)
        except Exception as e:
            print(f"  list start={start} err: {e}", file=sys.stderr)
            time.sleep(5)
            continue
        # total hit count
        if total is None:
            m = re.search(r'([0-9,]+)件中', html)
            if m:
                total = int(m.group(1).replace(",", ""))
                print(f"total hits: {total}", file=sys.stderr)
        items = parse_list(html)
        if not items:
            print(f"  start={start}: 0 items, stop", file=sys.stderr)
            break
        with open(LIST_JSONL, "a", encoding="utf-8") as f:
            for it in items:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
        total_collected += len(items)
        print(f"  start={start}: got {len(items)} total={total_collected}/{total}", file=sys.stderr)
        if total_collected >= (total or 0):
            break
        start += 20
        time.sleep(0.3)
    print(f"list done: {total_collected}", file=sys.stderr)

def fetch_details():
    if os.path.exists(DETAIL_JSONL):
        seen = set()
        for line in open(DETAIL_JSONL):
            seen.add(json.loads(line)["start"])
    else:
        seen = set()

    list_items = []
    for line in open(LIST_JSONL):
        list_items.append(json.loads(line))

    todo = [it for it in list_items if it["start"] not in seen]
    print(f"details: have {len(seen)}, need {len(todo)}", file=sys.stderr)
    for i, it in enumerate(todo):
        url = f"{BASE}/{it['detail_url_rel']}"
        try:
            html = fetch_sjis(url, timeout=20)
            d = parse_detail(html)
        except Exception as e:
            print(f"  detail start={it['start']} err: {e}", file=sys.stderr)
            continue
        rec = {**it, "detail": d}
        with open(DETAIL_JSONL, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if (i + 1) % 25 == 0:
            print(f"  detail {i+1}/{len(todo)}", file=sys.stderr)
        time.sleep(0.3)

def download_images():
    if not os.path.exists(DETAIL_JSONL):
        # fallback to list thumbs only
        items = [json.loads(l) for l in open(LIST_JSONL)]
    else:
        items = [json.loads(l) for l in open(DETAIL_JSONL)]
    ok = 0
    for i, it in enumerate(items):
        url = it.get("full_url") or it.get("thumb_url")
        if not url: continue
        pid = it["photo_id_num"]
        out = os.path.join(IMG_DIR, f"{pid}.jpg")
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            ok += 1
            continue
        try:
            data = fetch(url, timeout=20)
            if len(data) < 500: continue
            with open(out, "wb") as f:
                f.write(data)
            ok += 1
        except Exception as e:
            print(f"  img err {pid}: {e}", file=sys.stderr)
        if (i + 1) % 50 == 0:
            print(f"  img {i+1}/{len(items)} ok={ok}", file=sys.stderr)
        time.sleep(0.15)
    print(f"images: {ok}/{len(items)}", file=sys.stderr)

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("all", "list"):
        scrape_lists()
    if mode in ("all", "details"):
        fetch_details()
    if mode in ("all", "images"):
        download_images()
    print("=== DONE ===", file=sys.stderr)
    if os.path.exists(LIST_JSONL):
        print(f"list:    {sum(1 for _ in open(LIST_JSONL))}", file=sys.stderr)
    if os.path.exists(DETAIL_JSONL):
        print(f"details: {sum(1 for _ in open(DETAIL_JSONL))}", file=sys.stderr)
    print(f"images:  {len(os.listdir(IMG_DIR))}", file=sys.stderr)

if __name__ == "__main__":
    main()
