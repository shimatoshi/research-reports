#!/usr/bin/env python3
"""
Fetch all GBIF occurrence records for genus Rhinogobius.
API: https://api.gbif.org/v1
"""
import os, sys, json, time, urllib.request, urllib.parse

API = "https://api.gbif.org/v1"
OUT_DIR = "/tmp/gbif_out"
os.makedirs(OUT_DIR, exist_ok=True)
OCC_JSONL = os.path.join(OUT_DIR, "occurrences.jsonl")
SPECIES_JSON = os.path.join(OUT_DIR, "species.json")

UA = "rhinogobius-research/1.0 (+research use)"

def fetch_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

# 1. Resolve genus Rhinogobius taxonKey
def resolve_genus():
    data = fetch_json(f"{API}/species/match?name=Rhinogobius&rank=GENUS")
    print(f"genus match: usageKey={data.get('usageKey')} rank={data.get('rank')} status={data.get('status')}", file=sys.stderr)
    return data["usageKey"]

# 2. Enumerate species under genus
def list_species(genus_key):
    species = []
    offset = 0
    limit = 1000
    while True:
        url = f"{API}/species/{genus_key}/children?limit={limit}&offset={offset}"
        data = fetch_json(url)
        species.extend(data["results"])
        if data["endOfRecords"] or not data["results"]:
            break
        offset += limit
    print(f"species under genus: {len(species)}", file=sys.stderr)
    return species

# 3. Fetch occurrence records
def fetch_occurrences(genus_key, out_fp, page_size=300):
    offset = 0
    total_received = 0
    while True:
        url = f"{API}/occurrence/search?taxon_key={genus_key}&limit={page_size}&offset={offset}"
        try:
            data = fetch_json(url, timeout=60)
        except Exception as e:
            print(f"page offset={offset} error: {e}, retry in 5s", file=sys.stderr)
            time.sleep(5)
            continue
        results = data.get("results", [])
        for r in results:
            out_fp.write(json.dumps(r, ensure_ascii=False) + "\n")
        total_received += len(results)
        total = data.get("count", 0)
        print(f"  offset={offset} got={len(results)} accumulated={total_received}/{total}", file=sys.stderr)
        if data.get("endOfRecords") or len(results) == 0:
            break
        offset += page_size
        time.sleep(0.25)
    return total_received

def main():
    genus_key = resolve_genus()
    species = list_species(genus_key)
    with open(SPECIES_JSON, "w", encoding="utf-8") as f:
        json.dump(species, f, ensure_ascii=False, indent=1)
    print(f"saved {SPECIES_JSON}", file=sys.stderr)

    if os.path.exists(OCC_JSONL):
        os.remove(OCC_JSONL)
    with open(OCC_JSONL, "a", encoding="utf-8") as f:
        total = fetch_occurrences(genus_key, f)
    print(f"=== DONE === occurrences: {total}", file=sys.stderr)

if __name__ == "__main__":
    main()
