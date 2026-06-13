#!/usr/bin/env python3
"""Detect QR pages in a book PDF and group them into lessons.
Each lesson has 2 QR pages in reading order: Vocabulary (on the Word List start
page S) then Reading (on the reading start page R). So QR pages pair up as
(S1,R1,S2,R2,...). Word List = [S..R-1]; Reading = [R..exercise-1] (end found later).
Writes {letter}_qr.json. Usage: analyze_qr.py <letter> <pdf>
"""
import sys, json, fitz, cv2, numpy as np
from pathlib import Path

letter, pdf = sys.argv[1], sys.argv[2]
doc = fitz.open(pdf)
det = cv2.QRCodeDetector()
qr_pages = []
for i in range(doc.page_count):
    pix = doc[i].get_pixmap(dpi=300)
    arr = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
    arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR if pix.n == 4 else cv2.COLOR_RGB2BGR)
    ok, infos, _, _ = det.detectAndDecodeMulti(arr)
    if ok and any(s for s in infos):
        qr_pages.append(i + 1)

# pair into lessons
lessons = []
for k in range(0, len(qr_pages) - 1, 2):
    S, R = qr_pages[k], qr_pages[k + 1]
    lessons.append({"lesson": k // 2 + 1, "vocab_start": S, "reading_start": R,
                    "wordlist_pages": list(range(S, R))})
out = {"letter": letter, "pages": doc.page_count, "qr_pages": qr_pages,
       "n_qr": len(qr_pages), "n_lessons": len(lessons), "lessons": lessons}
Path(f"{letter}_qr.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
print(f"[{letter}] pages={doc.page_count} qr={len(qr_pages)} lessons={len(lessons)}")
print("  vocab_start:", [l["vocab_start"] for l in lessons])
print("  reading_start:", [l["reading_start"] for l in lessons])
print("  wordlist span sizes:", [len(l["wordlist_pages"]) for l in lessons])
