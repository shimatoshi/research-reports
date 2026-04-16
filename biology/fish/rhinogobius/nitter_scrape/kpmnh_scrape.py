#!/usr/bin/env python3
"""
KPMNH (神奈川県立生命の星・地球博物館) 収蔵資料検索システム scraper.
Targets: Rhinogobius (ヨシノボリ属) fish specimens.

- Search by Japanese name (c5_f) and Latin name (c6_f) on /list endpoint
- For each specimen pkey, fetch detail page
- Extract metadata + image URLs
- Download images
"""
import os, re, sys, json, time, urllib.parse, urllib.request, gzip, io
from html.parser import HTMLParser

BASE = "https://nh.kanagawa-museum.jp"
LIST_URL = BASE + "/kpmnh-collections/list"
DETAIL_URL = BASE + "/kpmnh-collections/detail"
MEDIA_URL = BASE + "/kpmnh-collections/rest/media"  # /S?cls=...&pkey=NNN  /L?... for large

OUT_DIR = "/tmp/kpmnh_out"
DETAILS_DIR = os.path.join(OUT_DIR, "details_html")
IMG_DIR = os.path.join(OUT_DIR, "images")
LIST_JSONL = os.path.join(OUT_DIR, "list.jsonl")
DETAIL_JSONL = os.path.join(OUT_DIR, "details.jsonl")
os.makedirs(DETAILS_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ja,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
        return data

def fetch_text(url, timeout=30):
    return fetch(url, timeout).decode("utf-8", errors="replace")

# --- Search URL builder ---
def build_list_url(field, value, pn=1, dispnum=500):
    """field is 'c5_f' (Japanese name) or 'c6_f' (Latin name)."""
    base_params = {
        "secIdx": "0", "cls": "collect_attfi", "pn": str(pn),
        "chkCls": "collect_attfi",
        "dispnum": str(dispnum), "sort": "", "order": "0",
    }
    # c1_a..c17_a default 1, c1_l..c17_l default 1 (c2_a=3, c2_l=2 from observed)
    for n in range(1, 18):
        base_params[f"c{n}_a"] = "3" if n == 2 else "1"
        base_params[f"c{n}_l"] = "2" if n == 2 else "1"
        base_params[f"c{n}_f"] = ""
    base_params[field] = value
    qs = urllib.parse.urlencode(base_params, encoding="utf-8")
    return f"{LIST_URL}?{qs}"

# --- List page parser ---
ROW_RE = re.compile(
    r'(KPM-NI\d+)</a>\s*</td>\s*'
    r'<td[^>]*>\s*<a[^>]+pkey=(\d+)[^>]*>([^<]*)</a>\s*</td>\s*'  # family ja
    r'<td[^>]*>\s*<a[^>]+>([^<]*)</a>\s*</td>\s*'                  # species ja
    r'<td[^>]*>\s*<a[^>]+>([^<]*)</a>\s*</td>\s*'                  # species latin
    r'<td[^>]*>\s*<a[^>]+>([^<]*)</a>\s*</td>'                     # locality
    , re.DOTALL)

def parse_list_page(html):
    rows = []
    for m in ROW_RE.finditer(html):
        rows.append({
            "kpm_id":   m.group(1),
            "pkey":     m.group(2),
            "family_ja": m.group(3).strip(),
            "name_ja":  m.group(4).strip(),
            "name_lat": m.group(5).strip(),
            "locality": m.group(6).strip(),
        })
    return rows

def page_count(html):
    nums = sorted({int(p) for p in re.findall(r'pn=(\d+)', html)})
    return max(nums) if nums else 1

# --- Detail page parser ---
def text(s): return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s)).strip()

def parse_detail(html, pkey):
    """Detail page is a table of <th>label</th><td>value</td>. Extract all pairs."""
    pairs = {}
    for m in re.finditer(r'<th[^>]*>(.+?)</th>\s*<td[^>]*>(.+?)</td>', html, re.DOTALL):
        k = text(m.group(1))
        v = text(m.group(2))
        if k and (k not in pairs or len(v) > len(pairs[k])):
            pairs[k] = v
    # Image URLs
    imgs = []
    for m in re.finditer(r'(/kpmnh-collections/rest/media/[A-Z][^"\']*pkey=(\d+)[^"\']*)', html):
        imgs.append(BASE + m.group(1).replace("&amp;", "&"))
    # Dedup preserving order
    imgs = list(dict.fromkeys(imgs))
    return {"pkey": pkey, "fields": pairs, "images": imgs}

# --- Main routines ---
def scrape_search(field, value, label):
    """Iterate all pages of one search, append rows to list.jsonl."""
    page = 1
    seen_pkeys = set()
    while True:
        url = build_list_url(field, value, pn=page, dispnum=500)
        try:
            html = fetch_text(url)
        except Exception as e:
            print(f"  [{label}] page {page} fetch error: {e}", file=sys.stderr)
            break
        rows = parse_list_page(html)
        new_rows = [r for r in rows if r["pkey"] not in seen_pkeys]
        for r in new_rows:
            r["search_field"] = field
            r["search_value"] = value
            r["search_label"] = label
            seen_pkeys.add(r["pkey"])
            with open(LIST_JSONL, "a") as f:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        max_page = page_count(html)
        print(f"  [{label}] page {page}/{max_page}: rows={len(rows)} new={len(new_rows)} total={len(seen_pkeys)}", file=sys.stderr)
        if page >= max_page or len(rows) == 0:
            break
        page += 1
        time.sleep(0.5)
    return seen_pkeys

def fetch_detail(pkey):
    url = f"{DETAIL_URL}?cls=collect_attfi&pkey={pkey}"
    cache = os.path.join(DETAILS_DIR, f"{pkey}.html")
    if os.path.exists(cache):
        return open(cache, "r", encoding="utf-8").read()
    html = fetch_text(url)
    with open(cache, "w", encoding="utf-8") as f:
        f.write(html)
    return html

def download_image(url, out_path):
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        return True
    try:
        data = fetch(url, timeout=30)
        with open(out_path, "wb") as f:
            f.write(data)
        return len(data) > 0
    except Exception as e:
        print(f"  img err {url}: {e}", file=sys.stderr)
        return False

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    if mode in ("all", "list"):
        if "--fresh" in sys.argv and os.path.exists(LIST_JSONL):
            os.remove(LIST_JSONL)
        # Search 1: Japanese name = ヨシノボリ (gets all species with the kana in their name)
        scrape_search("c5_f", "ヨシノボリ", "name_ja=ヨシノボリ")
        # Search 2: Latin name = Rhinogobius (covers anything Latin-only)
        scrape_search("c6_f", "Rhinogobius", "name_lat=Rhinogobius")

    if mode in ("all", "details"):
        # Load unique pkeys
        pkeys = set()
        for line in open(LIST_JSONL):
            pkeys.add(json.loads(line)["pkey"])
        already = set()
        if os.path.exists(DETAIL_JSONL):
            for line in open(DETAIL_JSONL):
                already.add(json.loads(line)["pkey"])
        todo = sorted(pkeys - already, key=int)
        print(f"detail: have {len(already)}, need {len(todo)}", file=sys.stderr)
        for i, pkey in enumerate(todo):
            try:
                html = fetch_detail(pkey)
                d = parse_detail(html, pkey)
                with open(DETAIL_JSONL, "a") as f:
                    f.write(json.dumps(d, ensure_ascii=False) + "\n")
            except Exception as e:
                print(f"  detail {pkey} err: {e}", file=sys.stderr)
            if (i + 1) % 25 == 0:
                print(f"  details: {i+1}/{len(todo)}", file=sys.stderr)
            time.sleep(0.3)

    if mode in ("all", "images"):
        jobs = []
        for line in open(DETAIL_JSONL):
            d = json.loads(line)
            for i, url in enumerate(d.get("images", [])):
                # Replace /S? (small) with /L? (large) when present
                large_url = re.sub(r"/rest/media/S\?", "/rest/media/L?", url)
                ext = "jpg"
                out_path = os.path.join(IMG_DIR, f"{d['pkey']}_{i}.{ext}")
                jobs.append((large_url, out_path))
        print(f"image jobs: {len(jobs)}", file=sys.stderr)
        ok = 0
        for i, (url, out) in enumerate(jobs):
            if download_image(url, out):
                ok += 1
            if (i + 1) % 50 == 0:
                print(f"  imgs: {i+1}/{len(jobs)} ok={ok}", file=sys.stderr)
            time.sleep(0.15)
        print(f"images ok: {ok}/{len(jobs)}", file=sys.stderr)

    print("=== DONE ===", file=sys.stderr)
    if os.path.exists(LIST_JSONL):
        print(f"list rows:    {sum(1 for _ in open(LIST_JSONL))}", file=sys.stderr)
    if os.path.exists(DETAIL_JSONL):
        print(f"details:      {sum(1 for _ in open(DETAIL_JSONL))}", file=sys.stderr)
    print(f"images:       {len(os.listdir(IMG_DIR))}", file=sys.stderr)

if __name__ == "__main__":
    main()
