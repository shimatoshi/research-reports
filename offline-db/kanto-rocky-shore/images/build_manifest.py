#!/usr/bin/env python3
"""Build MANIFEST.md from _manifest.json."""
import json, re, html
from pathlib import Path

OUT = Path("/home/kobayashi-takeru/work/shimatoshi/research-reports/biology/kanto-rocky-shore/images")
rows = json.loads((OUT / "_manifest.json").read_text())

def clean(s):
    if not s: return ""
    s = re.sub(r"<[^>]+>", " ", str(s))
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("|", "/")
    if len(s) > 140:
        s = s[:137] + "..."
    return s

# Count sources
wm_count = sum(1 for r in rows if "Wikimedia" in (r.get("notes") or ""))
inat_count = sum(1 for r in rows if "iNaturalist" in (r.get("notes") or ""))

md = []
md.append("# Kanto Rocky-Shore / Tidepool Organism Image Archive — MANIFEST")
md.append("")
md.append(f"- Total images: **{len(rows)}**")
md.append(f"- Sources: Wikimedia Commons = {wm_count}, iNaturalist = {inat_count}")
md.append(f"- User-Agent used: `KantoTidepoolResearch/1.0 (contact: kobayashit.prt@gmail.com)`")
md.append(f"- Download date: 2026-04-17")
md.append("")
md.append("## License notes")
md.append("- Wikimedia Commons images: CC licenses (CC-BY/BY-SA/PD/CC0 — see per-row column).")
md.append("- iNaturalist images: CC licenses (cc-by, cc-by-sa, cc-by-nc, cc-by-nc-sa, cc-by-nc-nd). **Non-commercial (NC) items cannot be used commercially** — check each row.")
md.append("- **ND (NoDerivatives)** items (3 photos): cannot be cropped/annotated/modified — use as-is only.")
md.append("- When reusing, cite the `source_url` and author fields exactly.")
md.append("")
md.append("## License distribution")
lic_counts = {}
for r in rows:
    l = r.get("license") or "UNKNOWN"
    lic_counts[l] = lic_counts.get(l, 0) + 1
for k in sorted(lic_counts, key=lambda x: -lic_counts[x]):
    md.append(f"- {k}: {lic_counts[k]}")
md.append("")
md.append("## Table")
md.append("")
md.append("| filename | 学名 | 和名 | license | author | source URL | description | notes |")
md.append("|---|---|---|---|---|---|---|---|")

# Sort rows by filename for readability
rows_sorted = sorted(rows, key=lambda r: r["filename"])
for r in rows_sorted:
    row = "| {fn} | {sci} | {ja} | {lic} | {au} | [link]({src}) | {desc} | {nt} |".format(
        fn=r["filename"],
        sci=clean(r.get("sci", "")),
        ja=clean(r.get("ja", "")),
        lic=clean(r.get("license", "")),
        au=clean(r.get("author", "")),
        src=r.get("source_url", ""),
        desc=clean(r.get("description", "")),
        nt=clean(r.get("notes", "")),
    )
    md.append(row)

(OUT / "MANIFEST.md").write_text("\n".join(md) + "\n")
print(f"Wrote MANIFEST.md with {len(rows)} rows")
print(f"WM={wm_count} iNat={inat_count}")
