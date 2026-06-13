#!/usr/bin/env python3
"""For each lesson, determine how many pages the reading passage spans (2 or 3).
Reading starts at S+2 (reading QR page). Send S+2,S+3,S+4 to Gemini, force it to
transcribe the opening body text, and count consecutive READING pages.
Reads {letter}_toc.json (list of {lesson,unit,title,start}); writes {letter}_spans.json.
Usage: classify_spans.py <letter> <pdf>
"""
import sys, json, os
from pathlib import Path
import fitz
from google import genai
from google.genai import types

letter, pdf = sys.argv[1], sys.argv[2]
toc = json.loads(Path(f"{letter}_toc.json").read_text())
doc = fitz.open(pdf)
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-2.5-flash"

PROMPT = (
    "3 consecutive scanned pages from a reading textbook. For EACH page return "
    '{"seq":n, "footer_page":<printed page number at bottom or null>, '
    '"first_body_text":"<first ~12 words of the main body text>", '
    '"type":"READING|EXERCISE|WORDLIST|OTHER"}. '
    "READING = narrative passage prose. EXERCISE = practice tasks ('Exercise', "
    "'Read the words in the box', a/b/c/d, 'Solve the puzzle', 'Comprehension', "
    "fill-in, circle T/F). A passage may span 2 OR 3 pages. Return ONLY a JSON array."
)

def part(pn):
    pix = doc[pn - 1].get_pixmap(dpi=150)
    return types.Part.from_bytes(data=pix.tobytes("jpeg"), mime_type="image/jpeg")

result = {}
for L in toc:
    s = L["start"]; pnums = [s + 2, s + 3, s + 4]
    arr = None
    for attempt in range(3):
        try:
            r = client.models.generate_content(
                model=MODEL, contents=[PROMPT + f"\nExpected printed numbers: {pnums}"] + [part(p) for p in pnums],
                config=types.GenerateContentConfig(response_mime_type="application/json"))
            arr = json.loads(r.text); break
        except Exception as e:
            print(f"  L{L['lesson']} attempt {attempt+1}: {str(e)[:60]}", flush=True)
    span = 2
    if arr and len(arr) >= 3 and str(arr[2].get("type", "")).upper() == "READING":
        span = 3
    reading_pages = [s + 2 + i for i in range(span)]
    result[str(L["lesson"])] = {"start": s, "reading_pages": reading_pages, "span": span,
                                "detail": arr}
    line = "  ".join(f"p{o.get('footer_page')}:{o.get('type','?')[:4]}" for o in (arr or []))
    print(f"L{L['lesson']:>2} S={s} reading={reading_pages} span={span} | {line}", flush=True)

Path(f"{letter}_spans.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(f"\nsaved {letter}_spans.json", flush=True)
