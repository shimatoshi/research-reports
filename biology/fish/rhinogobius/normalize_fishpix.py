#!/usr/bin/env python3
"""Normalize Fishpix records → common specimens schema."""
import os, re, json, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
FP_DIR = os.path.join(ROOT, "fishpix_raw")
DETAILS = os.path.join(FP_DIR, "details.jsonl")
IMG_DIR_REL = "fishpix_raw/images"
OUT_JSONL = os.path.join(ROOT, "specimens", "specimens.jsonl")
os.makedirs(os.path.dirname(OUT_JSONL), exist_ok=True)

ISLAND_SEP = re.compile(r'[；，,;]')

def split_locality(loc: str):
    if not loc: return []
    parts = [p.strip() for p in ISLAND_SEP.split(loc) if p.strip()]
    islands = []
    for p in parts:
        tail = p
        while tail:
            m = re.search(r'([^諸列]{1,10}(?:諸島|列島|島|半島))', tail)
            if not m or m.start() != 0:
                islands.append(tail); break
            islands.append(m.group(1))
            tail = tail[m.end():]
    return [i for i in islands if i]

def strip_authorship(lat_name: str) -> str:
    if not lat_name: return ""
    if "sp." in lat_name:
        m = re.match(r"^(\S+\s+sp\.\s*[A-Z]*\s*(?:\([^)]*\))?)", lat_name)
        if m: return m.group(1).strip()
    if "hybrid" in lat_name: return lat_name
    m = re.match(r"^([A-Z][a-z]+\s+[a-z]+(?:\s+[a-z]+)?)", lat_name)
    return m.group(1) if m else lat_name

# Pull prefecture from locality text
PREF_RE = re.compile(r'^([^県都府道；，,;]{1,5}[県都府道])')
def extract_prefecture(loc: str) -> str:
    if not loc: return ""
    m = PREF_RE.match(loc)
    return m.group(1) if m else ""

def repair_detail(d: dict) -> dict:
    """Fix the regex-mangled key for 撮影場所."""
    fixed = {}
    for k, v in d.items():
        if "撮影場所" in k and k != "撮影場所":
            fixed["撮影場所"] = v
        else:
            fixed[k] = v
    return fixed

n = 0
written = 0
loc_cnt = 0
img_cnt = 0
with open(OUT_JSONL, "a", encoding="utf-8") as out:
    for line in open(DETAILS):
        n += 1
        r = json.loads(line)
        d = repair_detail(r.get("detail", {}))
        loc = d.get("撮影場所", "")
        prefecture = extract_prefecture(loc)
        lat = d.get("species_lat_full") or r.get("lat", "")
        ja = d.get("species_ja_full") or r.get("ja", "")
        family_ja = d.get("family_ja", "")
        # Image file path relative to repo root
        img_rel = f"{IMG_DIR_REL}/{r['photo_id_num']}.jpg"
        has_image = os.path.exists(os.path.join(ROOT, img_rel))
        if has_image: img_cnt += 1
        if loc: loc_cnt += 1
        # note depth, notes
        depth = d.get("水深", "")
        notes = d.get("備考", "")

        rec = {
            "source": "fishpix",
            "source_id": r.get("kpm_nr_id", ""),
            "source_url": f"https://fishpix.kahaku.go.jp/fishimage/{r.get('detail_url_rel','')}",
            "species_ja": ja,
            "species_lat": lat,
            "species_lat_short": strip_authorship(lat),
            "family_ja": family_ja,
            "family_lat": "Gobiidae" if "ハゼ" in family_ja else "",
            "country": "日本国" if prefecture else "",
            "country_en": "Japan" if prefecture else "",
            "prefecture": prefecture,
            "prefecture_en": "",
            "locality_text": loc,
            "island_list": split_locality(loc),
            "lat": None, "lon": None,
            "date": d.get("撮影日", ""),
            "collector": d.get("撮影者", ""),
            "depth": depth,
            "notes": notes,
            "body_length_mm": None,
            "sex": "",
            "type_status": "",
            "images": [img_rel] if has_image else [],
            "has_image": has_image,
            "raw_ref": {"fishpix_photo_id": r.get("photo_id_num", ""), "start": r.get("start")},
        }
        out.write(json.dumps(rec, ensure_ascii=False) + "\n")
        written += 1

print(f"wrote {written} Fishpix records", file=sys.stderr)
print(f"  with locality: {loc_cnt}", file=sys.stderr)
print(f"  with image:    {img_cnt}", file=sys.stderr)
total = sum(1 for _ in open(OUT_JSONL))
print(f"specimens.jsonl total: {total}", file=sys.stderr)
