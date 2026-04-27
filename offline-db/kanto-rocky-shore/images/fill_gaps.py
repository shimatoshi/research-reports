#!/usr/bin/env python3
"""Fill gaps with iNaturalist + Wikimedia landscape images."""
import json, os, sys, time, urllib.parse, urllib.request
from pathlib import Path

UA = "KantoTidepoolResearch/1.0 (contact: kobayashit.prt@gmail.com)"
OUT = Path("/home/kobayashi-takeru/work/shimatoshi/research-reports/biology/kanto-rocky-shore/images")

# Species that missed
MISSED = [
    ("fish", "Enneapterygius", "etheostomus", "ヘビギンポ"),
    ("fish", "Pseudoblennius", "cottoides", "アナハゼ"),
    ("hermit", "Pagurus", "filholi", "ホンヤドカリ"),
    ("barnacle", "Fistulobalanus", "albicostatus", "シロスジフジツボ"),
    ("limpet", "Cellana", "toreuma", "ヨメガカサ"),
    ("chiton", "Placiphorella", "japonica", "ババガセ"),
    ("snail", "Chlorostoma", "xanthostigmum", "クマノコガイ"),
    ("snail", "Omphalius", "rusticus", "バテイラ"),
    ("nudibranch", "Hypselodoris", "festiva", "アオウミウシ"),
    ("cnid", "Anthopleura", "uchidai", "ヨロイイソギンチャク"),
    ("sponge", "Halichondria", "japonica", "ダイダイイソカイメン"),
    ("algae", "Gelidium", "elegans", "マクサ"),
]

# Kanto rocky-shore landscape queries
LANDSCAPES = [
    ("Jogashima", "城ヶ島"),
    ("Jogashima Island", "城ヶ島"),
    ("Arasaki Kanagawa", "荒崎"),
    ("Manazuru", "真鶴"),
    ("Mitsuishi Manazuru", "真鶴三ツ石"),
    ("Boso Peninsula coast", "房総"),
    ("Miura Peninsula coast", "三浦半島"),
    ("Katsuura Chiba coast", "勝浦"),
]

def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def download(url, path):
    try:
        data = http_get(url, timeout=60)
        if len(data) < 2000:
            return False, 0
        path.write_bytes(data)
        return True, len(data)
    except Exception as e:
        print(f"  dl error {url}: {e}", file=sys.stderr)
        return False, 0

def inat_observations(taxon_name):
    """Search iNaturalist observations by taxon name, filter CC licenses."""
    # First find taxon id
    q = urllib.parse.quote(taxon_name)
    try:
        d = json.loads(http_get(f"https://api.inaturalist.org/v1/taxa?q={q}&rank=species&per_page=5"))
        tid = None
        for r in d.get("results", []):
            if r.get("name", "").lower() == taxon_name.lower():
                tid = r["id"]
                break
        if not tid and d.get("results"):
            tid = d["results"][0]["id"]
        if not tid:
            return []
        # Query observations with CC license
        ou = f"https://api.inaturalist.org/v1/observations?taxon_id={tid}&photo_license=cc0,cc-by,cc-by-sa,cc-by-nc,cc-by-nc-sa&quality_grade=research&per_page=5&order_by=votes"
        od = json.loads(http_get(ou))
        photos = []
        for obs in od.get("results", []):
            for p in obs.get("photos", []):
                if p.get("license_code"):
                    orig = p.get("url", "").replace("/square.", "/original.")
                    photos.append({
                        "url": orig,
                        "license": p.get("license_code"),
                        "attribution": p.get("attribution"),
                        "page": f"https://www.inaturalist.org/observations/{obs.get('id')}",
                    })
                    break
            if len(photos) >= 2:
                break
        return photos
    except Exception as e:
        print(f"  inat obs error {taxon_name}: {e}", file=sys.stderr)
        return []

def inat_taxon_default(taxon_name):
    """Fallback: get default_photo of taxon."""
    q = urllib.parse.quote(taxon_name)
    try:
        d = json.loads(http_get(f"https://api.inaturalist.org/v1/taxa?q={q}&per_page=5"))
        for r in d.get("results", []):
            if r.get("name", "").lower() == taxon_name.lower():
                dp = r.get("default_photo")
                if dp:
                    url = dp.get("medium_url") or dp.get("original_url") or dp.get("url")
                    if url and "/square." in url:
                        url = url.replace("/square.", "/original.")
                    return {
                        "url": url,
                        "license": dp.get("license_code"),
                        "attribution": dp.get("attribution"),
                        "page": f"https://www.inaturalist.org/taxa/{r['id']}",
                    }
    except Exception as e:
        print(f"  inat default error: {e}", file=sys.stderr)
    return None

def ext_from_url(url):
    u = url.lower().split("?")[0]
    for e in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        if u.endswith(e):
            return e
    return ".jpg"

def wm_search(query, limit=5):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search&srnamespace=6&srsearch={urllib.parse.quote(query)}&srlimit={limit}"
    try:
        d = json.loads(http_get(url))
        return [r["title"] for r in d.get("query", {}).get("search", [])]
    except Exception as e:
        print(f"wm_search {query}: {e}", file=sys.stderr)
        return []

def wm_imageinfo(titles):
    if not titles:
        return []
    titles_param = "|".join(urllib.parse.quote(t) for t in titles)
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&titles={titles_param}&prop=imageinfo&iiprop=url|extmetadata|mime|size"
    try:
        d = json.loads(http_get(url))
        pages = d.get("query", {}).get("pages", {})
        out = []
        for _, page in pages.items():
            ii = page.get("imageinfo", [{}])[0]
            if not ii:
                continue
            md = ii.get("extmetadata", {})
            out.append({
                "title": page.get("title"),
                "url": ii.get("url"),
                "mime": ii.get("mime"),
                "license": md.get("LicenseShortName", {}).get("value", ""),
                "artist": md.get("Artist", {}).get("value", ""),
                "description": md.get("ImageDescription", {}).get("value", ""),
                "descriptionurl": ii.get("descriptionurl", ""),
            })
        return out
    except Exception as e:
        print(f"wm_imageinfo: {e}", file=sys.stderr)
        return []

def main():
    rows = []
    # Load existing manifest
    mjson = OUT / "_manifest.json"
    if mjson.exists():
        rows = json.loads(mjson.read_text())
    print(f"Existing rows: {len(rows)}")

    # Fill species gaps
    print("\n--- Species gap fill (iNaturalist + Wikimedia retry) ---")
    for group, genus, species, ja in MISSED:
        sci = f"{genus} {species}"
        # Retry Wikimedia first (429 earlier)
        titles = wm_search(sci, limit=4)
        infos = wm_imageinfo(titles[:3]) if titles else []
        infos = [i for i in infos if i.get("mime", "").startswith("image/")]
        got = False
        for info in infos[:1]:
            ext = ext_from_url(info["url"])
            fname = f"{group}_{genus}_{species}_1{ext}"
            fpath = OUT / fname
            ok, size = download(info["url"], fpath)
            if ok:
                rows.append({
                    "filename": fname, "sci": sci, "ja": ja,
                    "source_url": info["descriptionurl"] or info["url"],
                    "direct_url": info["url"], "license": info["license"],
                    "author": info["artist"][:200],
                    "description": (info["description"] or "")[:200],
                    "notes": f"Wikimedia Commons (retry). size={size}",
                })
                print(f"  WM retry OK: {sci}")
                got = True
                break
            time.sleep(0.3)
        if got:
            time.sleep(0.3)
            continue
        # iNat observations
        photos = inat_observations(sci)
        if not photos:
            dp = inat_taxon_default(sci)
            if dp:
                photos = [dp]
        if photos:
            p = photos[0]
            ext = ext_from_url(p["url"])
            fname = f"{group}_{genus}_{species}_inat1{ext}"
            fpath = OUT / fname
            ok, size = download(p["url"], fpath)
            if ok:
                rows.append({
                    "filename": fname, "sci": sci, "ja": ja,
                    "source_url": p["page"], "direct_url": p["url"],
                    "license": p["license"], "author": p["attribution"],
                    "description": "", "notes": f"iNaturalist. size={size}",
                })
                print(f"  iNat OK: {sci}")
            else:
                print(f"  iNat FAIL: {sci}")
        else:
            print(f"  MISS still: {sci}")
        time.sleep(0.5)

    # Landscape images
    print("\n--- Landscape images ---")
    seen_urls = set()
    landscape_count = 0
    for query, ja in LANDSCAPES:
        if landscape_count >= 8:
            break
        titles = wm_search(query, limit=6)
        infos = wm_imageinfo(titles[:4]) if titles else []
        infos = [i for i in infos if i.get("mime", "").startswith("image/")]
        site_key = query.lower().replace(" ", "-").split("-")[0]
        per_site = 0
        for info in infos:
            if per_site >= 2 or landscape_count >= 8:
                break
            if info["url"] in seen_urls:
                continue
            seen_urls.add(info["url"])
            ext = ext_from_url(info["url"])
            landscape_count += 1
            fname = f"landscape_{site_key}_{landscape_count}{ext}"
            fpath = OUT / fname
            ok, size = download(info["url"], fpath)
            if ok:
                rows.append({
                    "filename": fname, "sci": "-", "ja": f"景観: {ja}",
                    "source_url": info["descriptionurl"] or info["url"],
                    "direct_url": info["url"], "license": info["license"],
                    "author": info["artist"][:200],
                    "description": (info["description"] or "")[:200],
                    "notes": f"Wikimedia landscape. size={size}",
                })
                per_site += 1
                print(f"  LS OK: {fname}")
            else:
                landscape_count -= 1
            time.sleep(0.3)
        time.sleep(0.3)

    (OUT / "_manifest.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2))
    print(f"\nTotal rows: {len(rows)}")

if __name__ == "__main__":
    main()
