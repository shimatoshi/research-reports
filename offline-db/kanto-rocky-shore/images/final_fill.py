#!/usr/bin/env python3
"""Last-pass for 3 stubborn species."""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path

UA = "KantoTidepoolResearch/1.0 (contact: kobayashit.prt@gmail.com)"
OUT = Path("/home/kobayashi-takeru/work/shimatoshi/research-reports/biology/kanto-rocky-shore/images")

STUBBORN = [
    # (group, genus, species, ja, alt_queries, inat_search_terms)
    ("chiton", "Placiphorella", "japonica", "ババガセ",
     ["Placiphorella", "Acanthochitona"],
     ["Placiphorella japonica", "Placiphorella stimpsoni"]),
    ("snail", "Chlorostoma", "xanthostigmum", "クマノコガイ",
     ["Tegula xanthostigma", "Chlorostoma xanthostigma", "Tegula xanthostigmum"],
     ["Tegula xanthostigma", "Tegula xanthostigmum"]),
    ("cnid", "Anthopleura", "uchidai", "ヨロイイソギンチャク",
     ["Anthopleura uchidai", "Anthopleura japonica"],
     ["Anthopleura uchidai"]),
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
        print(f"  dl err: {e}", file=sys.stderr)
        return False, 0

def wm_search(q, limit=5):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search&srnamespace=6&srsearch={urllib.parse.quote(q)}&srlimit={limit}"
    try:
        d = json.loads(http_get(url))
        return [r["title"] for r in d.get("query", {}).get("search", [])]
    except:
        return []

def wm_imageinfo(titles):
    if not titles: return []
    tp = "|".join(urllib.parse.quote(t) for t in titles)
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&titles={tp}&prop=imageinfo&iiprop=url|extmetadata|mime"
    try:
        d = json.loads(http_get(url))
        out = []
        for _, p in d.get("query", {}).get("pages", {}).items():
            ii = p.get("imageinfo", [{}])[0]
            if not ii: continue
            md = ii.get("extmetadata", {})
            out.append({
                "title": p.get("title"), "url": ii.get("url"),
                "mime": ii.get("mime"),
                "license": md.get("LicenseShortName", {}).get("value", ""),
                "artist": md.get("Artist", {}).get("value", ""),
                "description": md.get("ImageDescription", {}).get("value", ""),
                "descriptionurl": ii.get("descriptionurl", ""),
            })
        return out
    except:
        return []

def inat_obs(name):
    q = urllib.parse.quote(name)
    try:
        d = json.loads(http_get(f"https://api.inaturalist.org/v1/taxa?q={q}&per_page=5"))
        tid = None
        for r in d.get("results", []):
            if name.lower() in r.get("name", "").lower():
                tid = r["id"]; break
        if not tid and d.get("results"):
            tid = d["results"][0]["id"]
        if not tid: return []
        ou = f"https://api.inaturalist.org/v1/observations?taxon_id={tid}&photo_license=cc0,cc-by,cc-by-sa,cc-by-nc,cc-by-nc-sa&per_page=5&order_by=votes"
        od = json.loads(http_get(ou))
        photos = []
        for obs in od.get("results", []):
            for p in obs.get("photos", []):
                if p.get("license_code"):
                    orig = p.get("url", "").replace("/square.", "/medium.")
                    photos.append({
                        "url": orig, "license": p.get("license_code"),
                        "attribution": p.get("attribution"),
                        "page": f"https://www.inaturalist.org/observations/{obs.get('id')}",
                    })
                    break
            if len(photos) >= 1: break
        return photos
    except Exception as e:
        print(f"  inat err {name}: {e}", file=sys.stderr)
        return []

def ext_from_url(url):
    u = url.lower().split("?")[0]
    for e in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        if u.endswith(e): return e
    return ".jpg"

rows = json.loads((OUT / "_manifest.json").read_text())
for group, genus, species, ja, alt_q, inat_q in STUBBORN:
    got = False
    for q in alt_q:
        titles = wm_search(q, limit=5)
        infos = wm_imageinfo(titles[:3])
        infos = [i for i in infos if i.get("mime", "").startswith("image/")]
        for info in infos[:1]:
            ext = ext_from_url(info["url"])
            fname = f"{group}_{genus}_{species}_1{ext}"
            fpath = OUT / fname
            ok, size = download(info["url"], fpath)
            if ok:
                rows.append({
                    "filename": fname, "sci": f"{genus} {species}", "ja": ja,
                    "source_url": info["descriptionurl"] or info["url"],
                    "direct_url": info["url"], "license": info["license"],
                    "author": info["artist"][:200],
                    "description": (info["description"] or "")[:200],
                    "notes": f"Wikimedia Commons (alt query: {q}). size={size}",
                })
                print(f"  WM OK via '{q}': {fname}")
                got = True
                break
        if got: break
        time.sleep(0.5)
    if got: continue
    # iNat fallback
    for q in inat_q:
        photos = inat_obs(q)
        if photos:
            p = photos[0]
            ext = ext_from_url(p["url"])
            fname = f"{group}_{genus}_{species}_inat1{ext}"
            fpath = OUT / fname
            ok, size = download(p["url"], fpath)
            if ok:
                rows.append({
                    "filename": fname, "sci": f"{genus} {species}", "ja": ja,
                    "source_url": p["page"], "direct_url": p["url"],
                    "license": p["license"], "author": p["attribution"],
                    "description": "", "notes": f"iNaturalist (query: {q}). size={size}",
                })
                print(f"  iNat OK via '{q}': {fname}")
                got = True
                break
        time.sleep(0.5)
    if not got:
        print(f"  STILL MISS: {genus} {species}")

(OUT / "_manifest.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2))
print(f"Total: {len(rows)}")
