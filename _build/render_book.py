#!/usr/bin/env python3
"""Render kept pages (Word List + Reading) from a book's source.pdf.
get_pixmap applies the page transform (correct orientation). Then ENHANCE for
readability (helps young/near-sighted readers): whiten the paper background,
lift contrast, boost colour, and sharpen text edges. High DPI + quality.
Reads {dir}/spec.json, writes {dir}/pages/pNNN.jpg.
Usage: render_book.py <book-dir> [dpi]
"""
import sys, json
from pathlib import Path
import fitz
from PIL import Image, ImageEnhance

bdir = Path(sys.argv[1])
DPI = int(sys.argv[2]) if len(sys.argv) > 2 else 200
spec = json.loads((bdir / "spec.json").read_text())
pages_dir = bdir / "pages"
pages_dir.mkdir(parents=True, exist_ok=True)
for f in pages_dir.glob("p*.*"):
    f.unlink()

def whiten(img, lo=14, hi=244):
    # linear level: map [lo,hi] -> [0,255] so off-white paper becomes pure white,
    # raising text contrast without crushing the photos.
    scale = 255.0 / (hi - lo)
    lut = [max(0, min(255, int((v - lo) * scale))) for v in range(256)]
    return img.point(lut * 3)

keep = sorted({p for L in spec for it in L["items"] for p in it["pages"]})
doc = fitz.open(str(bdir / "source.pdf"))
for pn in keep:
    pix = doc[pn - 1].get_pixmap(dpi=DPI)
    img = Image.frombytes("RGB" if pix.n < 4 else "RGBA",
                          [pix.width, pix.height], pix.samples).convert("RGB")
    img = whiten(img)
    img = ImageEnhance.Color(img).enhance(1.10)       # richer photo colour
    img = ImageEnhance.Contrast(img).enhance(1.05)
    img = ImageEnhance.Sharpness(img).enhance(1.6)     # crisper text edges
    img.save(pages_dir / f"p{pn:03d}.webp", "WEBP", quality=82, method=6)
sizes = [f.stat().st_size for f in pages_dir.glob("*.webp")]
print(f"{bdir.name}: rendered {len(keep)} pages @ {DPI}dpi (webp), "
      f"avg {sum(sizes)//len(sizes)//1024}KB, total {sum(sizes)//1024//1024}MB")
