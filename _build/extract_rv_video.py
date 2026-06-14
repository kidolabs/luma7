#!/usr/bin/env python3
"""Fetch a Reading for Vocabulary media page (worldcomedu), solve CUPID cookie,
extract per-lesson youtube id + Vocabulary/Reading mp3. Title is skipped (matched
but not captured) so apostrophe titles in double quotes (e.g. "We've Struck Gold!")
don't break the match. Writes {letter}_video.json. Usage: extract_rv_video.py <letter>
"""
import sys, re, json, subprocess, urllib.request

letter = sys.argv[1]
url = f"https://www.worldcomedu.com/media/reading-for-vocabulary-{letter}.html"
def get(u, ck=None):
    h = {"User-Agent": "Mozilla/5.0"}
    if ck: h["Cookie"] = ck
    return urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=30).read().decode("utf-8", "replace")

html = get(url)
if "slowAES" in html:
    n = re.findall(r'toNumbers\("([0-9a-f]{32})"\)', html)
    p = subprocess.run(f'printf {n[2]} | xxd -r -p | openssl enc -aes-128-cbc -d -K {n[0]} -iv {n[1]} -nopad | xxd -p',
                       shell=True, capture_output=True, text=True)
    html = get(url + "?ckattempt=1", "CUPID=" + p.stdout.strip().replace("\n", ""))

lessons = {}
# Just number -> youtube (anchored on lesson id; title skipped, both quote styles).
# Audio mapping is already correct in spec.json (verified), so tracks are not needed.
for m in re.finditer(
    r"id:\s*'unit[\d-]+',\s*number:\s*(\d+),\s*title:\s*(?:'[^']*'|\"[^\"]*\"),\s*"
    r"youtubeUs:\s*'https://youtu\.be/([A-Za-z0-9_-]{11})'",
    html, re.S):
    lessons[str(int(m.group(1)))] = {"youtube": m.group(2)}
json.dump({"letter": letter, "n": len(lessons), "lessons": lessons},
          open(f"{letter}_video.json", "w"), ensure_ascii=False, indent=2)
print(f"[{letter}] {len(lessons)} lessons with video")
for k in ["1", "2", "3", "4"]:
    L = lessons.get(k, {}); print(f"  L{k}: yt={L.get('youtube')} | {L.get('Vocabulary')}/{L.get('Reading')}")
