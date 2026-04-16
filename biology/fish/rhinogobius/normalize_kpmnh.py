#!/usr/bin/env python3
"""
Normalize KPMNH data → unified specimens schema.

Common schema per specimen:
{
  source: "kpmnh",
  source_id: "KPM-NI0003839",
  source_url: "https://nh.kanagawa-museum.jp/kpmnh-collections/detail?cls=collect_attfi&pkey=3839",
  species_ja: "オガサワラヨシノボリ",
  species_lat: "Rhinogobius ogasawaraensis Suzuki, Chen et Senou, 2011",
  species_lat_short: "Rhinogobius ogasawaraensis",   # stripped of authorship
  family_ja: "ハゼ科",
  family_lat: "Gobiidae",
  country: "日本国",
  country_en: "Japan",
  prefecture: "東京都",
  prefecture_en: "Tokyo Metropolis",
  locality_text: "東京都；小笠原諸島父島列島父島",
  island_list: ["小笠原諸島","父島列島","父島"],
  lat: null, lon: null,            # KPMNH doesn't publish coords
  date: null, collector: null,     # not published
  type_status: "非該当",
  images: ["kpmnh_specimens/images/3839.jpg"],
  has_image: true,
  raw_ref: {"list": "...#pkey=3839", "details": "...#pkey=3839"}
}
"""
import os, re, json, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
KPM_DIR = os.path.join(ROOT, "kpmnh_specimens")
LIST_JSONL = os.path.join(KPM_DIR, "list.jsonl")
DETAILS_JSONL = os.path.join(KPM_DIR, "details.jsonl")
IMGS_DIR = os.path.join(KPM_DIR, "images")
OUT_DIR = os.path.join(ROOT, "specimens")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_JSONL = os.path.join(OUT_DIR, "specimens.jsonl")

# Load all details by pkey
details = {}
for line in open(DETAILS_JSONL):
    d = json.loads(line)
    details[d["pkey"]] = d["fields"]

# Load list, one row per specimen (dedup by pkey, prefer first occurrence)
seen = set()
list_rows = {}
for line in open(LIST_JSONL):
    r = json.loads(line)
    pk = r["pkey"]
    if pk not in seen:
        seen.add(pk)
        list_rows[pk] = r

print(f"KPMNH: {len(list_rows)} unique pkeys, {len(details)} details", file=sys.stderr)

# Known locality separators (；, ，)
ISLAND_SEP = re.compile(r'[；，,;]')

def split_locality(loc: str):
    if not loc: return []
    # Split first by separator, then the remainder is still hierarchical (諸島 → 列島 → 島)
    parts = [p.strip() for p in ISLAND_SEP.split(loc) if p.strip()]
    islands = []
    for p in parts:
        # Further split on 諸島 / 列島 / 島 boundaries
        tail = p
        while tail:
            m = re.search(r'([^諸列]{1,10}(?:諸島|列島|島|半島))', tail)
            if not m or m.start() != 0:
                # prepend token that isn't island-typed
                # don't split further, just append the whole thing
                islands.append(tail)
                break
            islands.append(m.group(1))
            tail = tail[m.end():]
    # Cleanup: dedupe, strip trailing prefecture name
    return [i for i in islands if i]

def strip_authorship(lat_name: str) -> str:
    """'Rhinogobius ogasawaraensis Suzuki, Chen et Senou, 2011' -> 'Rhinogobius ogasawaraensis'"""
    if not lat_name: return ""
    # Handle sp. OR (morphotype ...) -> keep
    if "sp." in lat_name:
        m = re.match(r"^(\S+\s+sp\.\s*[A-Z]*\s*(?:\([^)]*\))?)", lat_name)
        if m: return m.group(1).strip()
    # hybrid complex
    if "hybrid" in lat_name: return lat_name
    # Normal: Genus species [subspecies] [(Authorship)]
    m = re.match(r"^([A-Z][a-z]+\s+[a-z]+(?:\s+[a-z]+)?)", lat_name)
    return m.group(1) if m else lat_name

count_imaged = 0
with open(OUT_JSONL, "w", encoding="utf-8") as out:
    for pk, r in list_rows.items():
        d = details.get(pk, {})
        loc = d.get("公開地域名（都道府県／島単位）[Locality]") or r.get("locality", "")
        prefecture = d.get("都道府県名", "") or r.get("locality", "").split("；")[0].split(",")[0]
        prefecture_en = d.get("Prefecture", "")
        img_path = os.path.join("kpmnh_specimens", "images", f"{pk}.jpg")
        has_image = os.path.exists(os.path.join(ROOT, img_path))
        if has_image: count_imaged += 1
        lat_name = r.get("name_lat", "")

        rec = {
            "source": "kpmnh",
            "source_id": r["kpm_id"],
            "source_url": f"https://nh.kanagawa-museum.jp/kpmnh-collections/detail?cls=collect_attfi&pkey={pk}",
            "species_ja": r.get("name_ja", ""),
            "species_lat": lat_name,
            "species_lat_short": strip_authorship(lat_name),
            "family_ja": r.get("family_ja", "") or d.get("科の和名（台帳上） [Japanese Name of Family]", ""),
            "family_lat": d.get("科の学名（台帳上） [Family Name]", ""),
            "country": d.get("国名", ""),
            "country_en": d.get("Country", ""),
            "prefecture": prefecture,
            "prefecture_en": prefecture_en,
            "locality_text": loc,
            "island_list": split_locality(loc),
            "lat": None, "lon": None,
            "date": None, "collector": None,
            "body_length_mm": None, "sex": None,
            "type_status": d.get("タイプ標本区分 [Type Status]", ""),
            "images": [img_path] if has_image else [],
            "has_image": has_image,
            "search_kw": r.get("search_label", ""),
            "raw_ref": {"pkey": pk},
        }
        out.write(json.dumps(rec, ensure_ascii=False) + "\n")

print(f"wrote {len(list_rows)} specimens -> {OUT_JSONL}", file=sys.stderr)
print(f"  with image: {count_imaged}", file=sys.stderr)
