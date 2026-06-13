#!/usr/bin/env python3
"""Combine {letter}_toc.json + {letter}_spans.json + {letter}_pagemap.json into
{bookdir}/spec.json. Lesson page numbers are PRINTED page numbers; we map each to
its real PDF index via the pagemap (scans can swap/drop pages). Pages are emitted
as PDF indices in PRINTED order.
Per lesson L: Word List = printed [S, S+1]; Reading = printed [S+2 .. S+1+span];
audio Vocabulary = track (2L-1), Reading = track (2L).
Usage: build_spec.py <letter> <book-dir>
"""
import sys, json
from pathlib import Path

letter, bdir = sys.argv[1], Path(sys.argv[2])
toc = json.loads(Path(f"{letter}_toc.json").read_text())
spans = json.loads(Path(f"{letter}_spans.json").read_text())
pm = json.loads(Path(f"{letter}_pagemap.json").read_text())["by_printed"]

def idx(printed):
    return pm.get(str(printed))   # PDF index (1-based) for a printed page, or None

spec = []; missing = []
for L in toc:
    n = L["lesson"]; s = L["start"]; span = spans[str(n)]["span"]
    wl_printed = [s, s + 1]
    rd_printed = [s + 2 + i for i in range(span)]
    def pages(printed_list):
        out = []
        for p in printed_list:
            j = idx(p)
            if j is None:
                missing.append((n, p))
            else:
                out.append(j)
        return out
    spec.append({
        "lesson": n, "unit": L["unit"], "title": L["title"],
        "items": [
            {"type": "Vocabulary", "printed": wl_printed, "pages": pages(wl_printed), "mp3": f"rv-{letter}-{2*n-1:02d}.mp3"},
            {"type": "Reading", "printed": rd_printed, "pages": pages(rd_printed), "mp3": f"rv-{letter}-{2*n:02d}.mp3"},
        ],
    })
(bdir / "spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2))
keep = sorted({p for Lx in spec for it in Lx["items"] for p in it["pages"]})
print(f"{bdir.name}: spec {len(spec)} lessons, {len(keep)} pages; missing={missing or 'none'}")
# show any lesson where printed order != index order (a swap was corrected)
for L in spec:
    for it in L["items"]:
        if it["pages"] != sorted(it["pages"]):
            print(f"  corrected order L{L['lesson']} {it['type']}: printed {it['printed']} -> idx {it['pages']}")
