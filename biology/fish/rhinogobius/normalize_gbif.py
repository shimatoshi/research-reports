#!/usr/bin/env python3
"""Normalize GBIF occurrence records → common specimens schema."""
import os, json, sys, re

ROOT = os.path.dirname(os.path.abspath(__file__))
GBIF_JSONL = os.path.join(ROOT, "gbif_raw", "occurrences.jsonl")
OUT_JSONL = os.path.join(ROOT, "specimens", "specimens.jsonl")
os.makedirs(os.path.dirname(OUT_JSONL), exist_ok=True)

# Read existing specimens (KPMNH) to append
existing_count = 0
if os.path.exists(OUT_JSONL):
    with open(OUT_JSONL) as f:
        existing_count = sum(1 for _ in f)
print(f"existing specimens in {OUT_JSONL}: {existing_count}", file=sys.stderr)

def strip_authorship(lat_name: str) -> str:
    if not lat_name: return ""
    if "sp." in lat_name:
        m = re.match(r"^(\S+\s+sp\.\s*[A-Z]*\s*(?:\([^)]*\))?)", lat_name)
        if m: return m.group(1).strip()
    if "hybrid" in lat_name: return lat_name
    m = re.match(r"^([A-Z][a-z]+\s+[a-z]+(?:\s+[a-z]+)?)", lat_name)
    return m.group(1) if m else lat_name

counts = {"ja": 0, "obs": 0, "specimen": 0, "has_coord": 0, "has_image": 0, "country": {}, "basis": {}}
written = 0
with open(OUT_JSONL, "a", encoding="utf-8") as out:
    with open(GBIF_JSONL) as f:
        for line in f:
            try:
                o = json.loads(line)
            except:
                continue
            lat = o.get("decimalLatitude")
            lon = o.get("decimalLongitude")
            sci = o.get("scientificName", "") or o.get("acceptedScientificName", "")
            species = o.get("species", "")
            country = o.get("country", "")
            state = o.get("stateProvince", "") or o.get("verbatimStateProvince", "")
            locality = o.get("locality", "") or o.get("verbatimLocality", "")
            date = o.get("eventDate", "") or str(o.get("year", "") or "")
            recorded_by = o.get("recordedBy", "")
            institution = o.get("institutionCode", "")
            collection = o.get("collectionCode", "")
            catno = o.get("catalogNumber", "")
            basis = o.get("basisOfRecord", "")
            type_status = o.get("typeStatus", "")
            media = []
            for m in o.get("media", []) or []:
                if m.get("identifier"): media.append(m["identifier"])
            rec = {
                "source": "gbif",
                "source_id": str(o.get("key", "")),
                "source_url": f"https://www.gbif.org/occurrence/{o.get('key')}" if o.get("key") else "",
                "species_ja": "",
                "species_lat": sci,
                "species_lat_short": strip_authorship(species or sci),
                "family_ja": "",
                "family_lat": o.get("family", ""),
                "country": country,
                "country_en": country,
                "prefecture": state,
                "prefecture_en": state,
                "locality_text": locality,
                "island_list": [],
                "lat": lat,
                "lon": lon,
                "date": date,
                "collector": recorded_by,
                "body_length_mm": None,
                "sex": o.get("sex", ""),
                "type_status": type_status,
                "institution_code": institution,
                "collection_code": collection,
                "catalog_number": catno,
                "basis_of_record": basis,
                "images": media,
                "has_image": len(media) > 0,
                "gbif_dataset": o.get("datasetName", "") or o.get("datasetKey", ""),
                "publishing_country": o.get("publishingCountry", ""),
                "raw_ref": {"gbif_key": o.get("key")},
            }
            # country JP?
            if country == "JP" or country == "Japan" or "Japan" in country:
                counts["ja"] += 1
            counts["country"][country] = counts["country"].get(country, 0) + 1
            counts["basis"][basis] = counts["basis"].get(basis, 0) + 1
            if basis == "HUMAN_OBSERVATION": counts["obs"] += 1
            elif basis == "PRESERVED_SPECIMEN": counts["specimen"] += 1
            if lat is not None and lon is not None: counts["has_coord"] += 1
            if rec["has_image"]: counts["has_image"] += 1
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            written += 1

print(f"wrote {written} GBIF records", file=sys.stderr)
print(f"  with coords: {counts['has_coord']}", file=sys.stderr)
print(f"  with image:  {counts['has_image']}", file=sys.stderr)
print(f"  Japan:       {counts['ja']}", file=sys.stderr)
print("  top countries:", sorted(counts['country'].items(), key=lambda x: -x[1])[:10], file=sys.stderr)
print("  basis:", counts['basis'], file=sys.stderr)
print(f"total specimens now: {existing_count + written}", file=sys.stderr)
