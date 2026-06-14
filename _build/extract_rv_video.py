#!/usr/bin/env python3
"""Fetch a Reading for Vocabulary media page (worldcomedu), solve the CUPID cookie,
and extract per-lesson: number, title, youtubeUs id, Vocabulary/Reading mp3.
Writes {letter}_video.json. Usage: extract_rv_video.py <letter>
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
# each lesson object: id, number, title, youtubeUs, ... tracks Vocabulary/Reading
for m in re.finditer(
    r"\{\s*id:\s*'[^']+',\s*number:\s*(\d+),\s*title:\s*'([^']*)',\s*youtubeUs:\s*'https://youtu\.be/([A-Za-z0-9_-]{11})'.*?tracks:\s*\[(.*?)\]\s*\}",
    html, re.S):
    num = int(m.group(1)); title = m.group(2).strip(); yid = m.group(3); tr = m.group(4)
    parts = dict((lab.split('—')[-1].strip(), mp3.split('/')[-1])
                 for lab, mp3 in re.findall(r"\['([^']+)',\s*'mp3/[^']+/([^']+)'\]", tr))
    lessons[str(num)] = {"title": title, "youtube": yid,
                         "Vocabulary": parts.get("Vocabulary"), "Reading": parts.get("Reading")}
json.dump({"letter": letter, "n": len(lessons), "lessons": lessons},
          open(f"{letter}_video.json", "w"), ensure_ascii=False, indent=2)
print(f"[{letter}] {len(lessons)} lessons with video")
for k in list(lessons)[:2] + [str(len(lessons))]:
    L = lessons.get(k, {})
    print(f"  L{k}: {L.get('title')} | yt={L.get('youtube')} | {L.get('Vocabulary')}/{L.get('Reading')}")
