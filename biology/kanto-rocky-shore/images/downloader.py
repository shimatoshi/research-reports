#!/usr/bin/env python3
"""Kanto rocky-shore species image downloader.
Primary: Wikimedia Commons. Secondary: iNaturalist.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import concurrent.futures
from pathlib import Path

UA = "KantoTidepoolResearch/1.0 (contact: kobayashit.prt@gmail.com)"
OUT = Path("/home/kobayashi-takeru/work/shimatoshi/research-reports/biology/kanto-rocky-shore/images")
OUT.mkdir(parents=True, exist_ok=True)

# (group_prefix, genus, species, japanese_name)
SPECIES = [
    # Fish
    ("fish", "Chasmichthys", "gulosus", "ドロメ"),
    ("fish", "Chaenogobius", "annularis", "アゴハゼ"),
    ("fish", "Bathygobius", "fuscus", "クモハゼ"),
    ("fish", "Eviota", "abax", "イソハゼ"),
    ("fish", "Omobranchus", "elegans", "ナベカ"),
    ("fish", "Petroscirtes", "breviceps", "ニジギンポ"),
    ("fish", "Enneapterygius", "etheostomus", "ヘビギンポ"),
    ("fish", "Hexagrammos", "agrammus", "クジメ"),
    ("fish", "Hypodytes", "rubripinnis", "ハオコゼ"),
    ("fish", "Girella", "punctata", "メジナ"),
    ("fish", "Pseudoblennius", "cottoides", "アナハゼ"),
    # Crabs
    ("crab", "Hemigrapsus", "sanguineus", "イソガニ"),
    ("crab", "Hemigrapsus", "takanoi", "ケフサイソガニ"),
    ("crab", "Pachygrapsus", "crassipes", "イワガニ"),
    ("crab", "Gaetice", "depressus", "ヒライソガニ"),
    ("crab", "Plagusia", "dentipes", "ショウジンガニ"),
    ("crab", "Charybdis", "japonica", "イシガニ"),
    ("crab", "Parasesarma", "pictum", "カクベンケイガニ"),
    # Hermit crabs / shrimp
    ("hermit", "Pagurus", "filholi", "ホンヤドカリ"),
    ("hermit", "Pagurus", "minutus", "ユビナガホンヤドカリ"),
    ("hermit", "Clibanarius", "virescens", "イソヨコバサミ"),
    ("shrimp", "Palaemon", "pacificus", "イソスジエビ"),
    # Barnacles / isopods
    ("barnacle", "Chthamalus", "challengeri", "イワフジツボ"),
    ("barnacle", "Fistulobalanus", "albicostatus", "シロスジフジツボ"),
    ("barnacle", "Tetraclita", "japonica", "クロフジツボ"),
    ("barnacle", "Capitulum", "mitella", "カメノテ"),
    ("isopod", "Ligia", "exotica", "フナムシ"),
    # Limpets / chitons / snails
    ("limpet", "Cellana", "nigrolineata", "マツバガイ"),
    ("limpet", "Cellana", "toreuma", "ヨメガカサ"),
    ("limpet", "Patelloida", "saccharina", "ウノアシ"),
    ("chiton", "Placiphorella", "japonica", "ババガセ"),
    ("snail", "Littorina", "brevicula", "タマキビ"),
    ("snail", "Reishia", "clavigera", "イボニシ"),
    ("snail", "Chlorostoma", "xanthostigmum", "クマノコガイ"),
    ("snail", "Omphalius", "rusticus", "バテイラ"),
    ("snail", "Lunella", "coreensis", "スガイ"),
    # Nudibranchs
    ("nudibranch", "Hypselodoris", "festiva", "アオウミウシ"),
    ("nudibranch", "Chromodoris", "orientalis", "シロウミウシ"),
    # Bivalves
    ("bivalve", "Magallana", "gigas", "マガキ"),
    ("bivalve", "Mytilus", "galloprovincialis", "ムラサキイガイ"),
    # Cephalopods
    ("ceph", "Octopus", "sinensis", "イイダコ"),
    ("ceph", "Hapalochlaena", "fasciata", "ヒョウモンダコ"),
    # Echinoderms
    ("echino", "Heliocidaris", "crassispina", "ムラサキウニ"),
    ("echino", "Hemicentrotus", "pulcherrimus", "バフンウニ"),
    ("echino", "Diadema", "setosum", "ガンガゼ"),
    ("echino", "Patiria", "pectinifera", "イトマキヒトデ"),
    ("echino", "Asterias", "amurensis", "マヒトデ"),
    ("echino", "Coscinasterias", "acutispina", "ヤツデヒトデ"),
    ("echino", "Apostichopus", "japonicus", "マナマコ"),
    ("echino", "Ophioplocus", "japonicus", "ニホンクモヒトデ"),
    # Cnidarians
    ("cnid", "Anthopleura", "fuscoviridis", "ミドリイソギンチャク"),
    ("cnid", "Anthopleura", "uchidai", "ヨロイイソギンチャク"),
    ("cnid", "Diadumene", "lineata", "タテジマイソギンチャク"),
    # Worms / sponges / tunicates
    ("worm", "Sabellastarte", "japonica", "ケヤリムシ"),
    ("sponge", "Halichondria", "japonica", "ダイダイイソカイメン"),
    ("tunicate", "Halocynthia", "roretzi", "マボヤ"),
    # Algae
    ("algae", "Ulva", "australis", "アナアオサ"),
    ("algae", "Codium", "fragile", "ミル"),
    ("algae", "Eisenia", "bicyclis", "アラメ"),
    ("algae", "Ecklonia", "cava", "カジメ"),
    ("algae", "Undaria", "pinnatifida", "ワカメ"),
    ("algae", "Sargassum", "fusiforme", "ヒジキ"),
    ("algae", "Sargassum", "horneri", "アカモク"),
    ("algae", "Gelidium", "elegans", "マクサ"),
    ("algae", "Corallina", "pilulifera", "ピリヒバ"),
    ("algae", "Gloiopeltis", "furcata", "フノリ"),
    ("algae", "Padina", "arborescens", "ウミウチワ"),
]

def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def wm_search(query, limit=3):
    """Search Wikimedia Commons for files in File namespace."""
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search&srnamespace=6&srsearch={urllib.parse.quote(query)}&srlimit={limit}"
    try:
        d = json.loads(http_get(url))
        return [r["title"] for r in d.get("query", {}).get("search", [])]
    except Exception as e:
        print(f"  wm_search error for {query}: {e}", file=sys.stderr)
        return []

def wm_imageinfo(titles):
    """Fetch imageinfo for given File: titles. Returns list of dicts."""
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
                "width": ii.get("width"),
                "height": ii.get("height"),
                "license": md.get("LicenseShortName", {}).get("value", ""),
                "artist": md.get("Artist", {}).get("value", ""),
                "description": md.get("ImageDescription", {}).get("value", ""),
                "descriptionurl": ii.get("descriptionurl", ""),
            })
        return out
    except Exception as e:
        print(f"  wm_imageinfo error: {e}", file=sys.stderr)
        return []

def inat_taxon_photo(name):
    """Query iNaturalist taxa endpoint for default_photo. Returns (url, license, attribution, inat_url)."""
    q = urllib.parse.quote(name)
    url = f"https://api.inaturalist.org/v1/taxa?q={q}&rank=species&per_page=5"
    try:
        d = json.loads(http_get(url))
        for r in d.get("results", []):
            if r.get("name", "").lower() == name.lower():
                dp = r.get("default_photo")
                if dp and dp.get("license_code") in ("cc0", "cc-by", "cc-by-sa", "cc-by-nc", "cc-by-nc-sa"):
                    return (dp.get("medium_url") or dp.get("original_url") or dp.get("url"),
                            dp.get("license_code"),
                            dp.get("attribution"),
                            f"https://www.inaturalist.org/taxa/{r.get('id')}")
        # fallback: first match
        if d.get("results"):
            r = d["results"][0]
            dp = r.get("default_photo")
            if dp and dp.get("license_code"):
                return (dp.get("medium_url") or dp.get("original_url") or dp.get("url"),
                        dp.get("license_code"),
                        dp.get("attribution"),
                        f"https://www.inaturalist.org/taxa/{r.get('id')}")
    except Exception as e:
        print(f"  inat error for {name}: {e}", file=sys.stderr)
    return None

def download(url, path):
    """Download url to path."""
    try:
        data = http_get(url, timeout=60)
        if len(data) < 2000:
            return False, 0
        path.write_bytes(data)
        return True, len(data)
    except Exception as e:
        print(f"  download error {url}: {e}", file=sys.stderr)
        return False, 0

def ext_from_url(url):
    u = url.lower().split("?")[0]
    for e in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        if u.endswith(e):
            return e
    return ".jpg"

def fetch_species(entry, idx):
    """Returns list of manifest rows."""
    group, genus, species, ja = entry
    sci = f"{genus} {species}"
    rows = []
    # Try Wikimedia first
    titles = wm_search(sci, limit=5)
    infos = wm_imageinfo(titles[:3]) if titles else []
    # Filter to image mimes
    infos = [i for i in infos if i.get("mime", "").startswith("image/")]
    count = 0
    for info in infos:
        if count >= 2:
            break
        ext = ext_from_url(info["url"])
        fname = f"{group}_{genus}_{species}_{count+1}{ext}"
        fpath = OUT / fname
        ok, size = download(info["url"], fpath)
        if ok:
            rows.append({
                "filename": fname,
                "sci": sci,
                "ja": ja,
                "source_url": info["descriptionurl"] or info["url"],
                "direct_url": info["url"],
                "license": info["license"],
                "author": info["artist"][:200],
                "description": (info["description"] or "")[:200],
                "notes": f"Wikimedia Commons. size={size}",
            })
            count += 1
            time.sleep(0.1)
    # If no Wikimedia hits, try iNaturalist
    if count == 0:
        inat = inat_taxon_photo(sci)
        if inat:
            iurl, ilic, iattr, ipage = inat
            # medium_url is square thumbnail; prefer original_url if present
            url_to_use = iurl.replace("/medium.", "/original.") if "/medium." in iurl else iurl
            ext = ext_from_url(url_to_use)
            fname = f"{group}_{genus}_{species}_1{ext}"
            fpath = OUT / fname
            ok, size = download(url_to_use, fpath)
            if not ok and url_to_use != iurl:
                ok, size = download(iurl, fpath)
            if ok:
                rows.append({
                    "filename": fname,
                    "sci": sci,
                    "ja": ja,
                    "source_url": ipage,
                    "direct_url": url_to_use,
                    "license": ilic,
                    "author": iattr,
                    "description": "",
                    "notes": f"iNaturalist. size={size}",
                })
    return rows

def main():
    all_rows = []
    print(f"Processing {len(SPECIES)} species...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(fetch_species, e, i): e for i, e in enumerate(SPECIES)}
        done = 0
        for fut in concurrent.futures.as_completed(futs):
            e = futs[fut]
            try:
                rows = fut.result()
                all_rows.extend(rows)
                done += 1
                status = "OK" if rows else "MISS"
                print(f"[{done}/{len(SPECIES)}] {status} {e[1]} {e[2]} ({e[3]}) -> {len(rows)} imgs")
            except Exception as ex_:
                print(f"ERROR {e}: {ex_}", file=sys.stderr)
    # Write intermediate json
    (OUT / "_manifest.json").write_text(json.dumps(all_rows, ensure_ascii=False, indent=2))
    print(f"\nTotal rows: {len(all_rows)}")

if __name__ == "__main__":
    main()
