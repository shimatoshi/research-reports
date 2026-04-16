#!/usr/bin/env python3
"""
Fetch list of pkeys that have actual images (imginfo=on filter), then download L size.
"""
import os, re, sys, json, time, urllib.parse, urllib.request, gzip

BASE = "https://nh.kanagawa-museum.jp"
LIST_URL = BASE + "/kpmnh-collections/list"
MEDIA_URL = BASE + "/kpmnh-collections/rest/media"

OUT_DIR = "/tmp/kpmnh_out"
IMG_DIR = os.path.join(OUT_DIR, "images")
IMAGED_PKEYS = os.path.join(OUT_DIR, "imaged_pkeys.json")
os.makedirs(IMG_DIR, exist_ok=True)

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ja,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            d = gzip.decompress(d)
        return d

def fetch_text(url, timeout=30):
    return fetch(url, timeout).decode("utf-8", errors="replace")

def build_list_url(field, value, pn=1, dispnum=500):
    p = {
        "secIdx": "0", "cls": "collect_attfi", "pn": str(pn),
        "chkCls": "collect_attfi",
        "imginfo": "on",
        "dispnum": str(dispnum), "sort": "", "order": "0",
    }
    for n in range(1, 18):
        p[f"c{n}_a"] = "3" if n == 2 else "1"
        p[f"c{n}_l"] = "2" if n == 2 else "1"
        p[f"c{n}_f"] = ""
    p[field] = value
    return f"{LIST_URL}?{urllib.parse.urlencode(p, encoding='utf-8')}"

def collect_imaged_pkeys():
    """Search both ヨシノボリ (ja) and Rhinogobius (lat) with imginfo=on, dedup pkeys."""
    pkeys = {}  # pkey -> some sample row dict
    for field, value, label in [("c5_f", "ヨシノボリ", "name_ja=ヨシノボリ"),
                                 ("c6_f", "Rhinogobius", "name_lat=Rhinogobius")]:
        page = 1
        while True:
            url = build_list_url(field, value, pn=page, dispnum=500)
            html = fetch_text(url)
            rows = re.findall(
                r'(KPM-NI\d+)</a>\s*</td>\s*'
                r'<td[^>]*>\s*<a[^>]+pkey=(\d+)[^>]*>([^<]*)</a>\s*</td>\s*'
                r'<td[^>]*>\s*<a[^>]+>([^<]*)</a>\s*</td>\s*'
                r'<td[^>]*>\s*<a[^>]+>([^<]*)</a>\s*</td>\s*'
                r'<td[^>]*>\s*<a[^>]+>([^<]*)</a>\s*</td>',
                html, re.DOTALL)
            new = 0
            for kpm, pkey, fam, nj, nl, loc in rows:
                if pkey not in pkeys:
                    pkeys[pkey] = {"kpm_id": kpm, "pkey": pkey, "family_ja": fam.strip(),
                                   "name_ja": nj.strip(), "name_lat": nl.strip(), "locality": loc.strip()}
                    new += 1
            page_nums = sorted({int(p) for p in re.findall(r'pn=(\d+)', html)})
            max_page = page_nums[-1] if page_nums else 1
            print(f"  [{label}] pn{page}/{max_page}: rows={len(rows)} new={new} total={len(pkeys)}", file=sys.stderr)
            if page >= max_page or len(rows) == 0:
                break
            page += 1
            time.sleep(0.5)
    return pkeys

def download_image(pkey, out_path, size="L"):
    if os.path.exists(out_path) and os.path.getsize(out_path) > 5000:
        return True  # already downloaded a non-placeholder
    url = f"{MEDIA_URL}/{size}?cls=collect_attfi&pkey={pkey}"
    try:
        data = fetch(url, timeout=20)
        if len(data) < 100:
            return False
        with open(out_path, "wb") as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"  img err {pkey}: {e}", file=sys.stderr)
        return False

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("all", "pkeys"):
        if os.path.exists(IMAGED_PKEYS) and "--fresh" not in sys.argv:
            pkeys = json.load(open(IMAGED_PKEYS))
            print(f"reusing {len(pkeys)} pkeys from cache", file=sys.stderr)
        else:
            pkeys = collect_imaged_pkeys()
            with open(IMAGED_PKEYS, "w") as f:
                json.dump(pkeys, f, ensure_ascii=False, indent=1)
            print(f"saved {len(pkeys)} imaged-pkeys to {IMAGED_PKEYS}", file=sys.stderr)

    if mode in ("all", "download"):
        pkeys = json.load(open(IMAGED_PKEYS))
        items = sorted(pkeys.items(), key=lambda kv: int(kv[0]))
        print(f"downloading {len(items)} images...", file=sys.stderr)
        ok = 0
        for i, (pkey, row) in enumerate(items):
            out = os.path.join(IMG_DIR, f"{pkey}.jpg")
            if download_image(pkey, out, "L"):
                ok += 1
            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{len(items)} ok={ok}", file=sys.stderr)
            time.sleep(0.15)
        print(f"images ok: {ok}/{len(items)}", file=sys.stderr)

    print("=== DONE ===", file=sys.stderr)
    print(f"images dir: {len(os.listdir(IMG_DIR))} files", file=sys.stderr)

if __name__ == "__main__":
    main()
