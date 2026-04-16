#!/usr/bin/env python3
"""Normalize S-Net list → specimens schema."""
import os, re, json, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SNET_LIST = os.path.join(ROOT, "snet_raw", "list.jsonl")
OUT = os.path.join(ROOT, "specimens", "specimens.jsonl")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

def strip_authorship(lat):
    if not lat: return ""
    if "sp." in lat:
        m = re.match(r"^(\S+\s+sp\.\s*[A-Za-z0-9]*\s*(?:\([^)]*\))?)", lat)
        if m: return m.group(1).strip()
    if "hybrid" in lat: return lat
    m = re.match(r"^([A-Z][a-z]+\s+[a-z]+(?:\s+[a-z]+)?)", lat)
    return m.group(1) if m else lat

ISLAND_SEP = re.compile(r'[；，,;]')
def split_locality(loc):
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

n = 0
inst_counts = {}
with open(OUT, "a", encoding="utf-8") as out:
    for line in open(SNET_LIST):
        r = json.loads(line)
        c = r["cells"]
        if len(c) < 8: continue
        # cell layout: [_, row#, 学名, 和名, 資料番号, 国, 都道府県, 収蔵機関, _]
        lat = c[2] or ""
        ja = c[3] or ""
        cat_no = c[4] or ""
        country = c[5] or ""
        prefecture = c[6] or ""
        institution = c[7] or ""
        inst_counts[institution] = inst_counts.get(institution, 0) + 1
        rec = {
            "source": "snet",
            "source_id": f"snet:{r['pkey']}",
            "source_url": f"https://science-net.kahaku.go.jp/search/detail?cls=collect11&pkey={r['pkey']}",
            "species_ja": ja,
            "species_lat": lat,
            "species_lat_short": strip_authorship(lat),
            "family_ja": "ハゼ科" if "Rhinogobius" in lat else "",
            "family_lat": "Gobiidae" if "Rhinogobius" in lat else "",
            "country": country,
            "country_en": "Japan" if country == "日本" else country,
            "prefecture": prefecture,
            "prefecture_en": "",
            "locality_text": prefecture,
            "island_list": split_locality(prefecture),
            "lat": None, "lon": None,
            "date": None, "collector": None,
            "body_length_mm": None, "sex": "",
            "type_status": "",
            "institution": institution,
            "catalog_number": cat_no if cat_no and cat_no != "******" else "",
            "images": [],
            "has_image": False,
            "raw_ref": {"snet_pkey": r["pkey"]},
        }
        out.write(json.dumps(rec, ensure_ascii=False) + "\n")
        n += 1

print(f"wrote {n} S-Net records", file=sys.stderr)
total = sum(1 for _ in open(OUT))
print(f"specimens.jsonl total: {total}", file=sys.stderr)
