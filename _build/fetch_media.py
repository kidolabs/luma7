#!/usr/bin/env python3
"""For a WorldCom media page (per book), solve the slowAES CUPID cookie challenge,
refetch, and extract the MP3 playlist (label -> mp3 path). Prints JSON.
Usage: fetch_media.py <book-letter>   e.g. fetch_media.py b
"""
import sys, re, subprocess, json, urllib.request

letter = sys.argv[1].lower()
URL = f"https://www.worldcomedu.com/media/reading-for-vocabulary-{letter}.html"
UA = "Mozilla/5.0"

def get(url, cookie=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA,
        **({"Cookie": cookie} if cookie else {})})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

def solve_cookie(html):
    a = re.search(r'toNumbers\("([0-9a-f]{32})"\)', html)
    nums = re.findall(r'toNumbers\("([0-9a-f]{32})"\)', html)
    if len(nums) < 3:
        return None
    key, iv, ct = nums[0], nums[1], nums[2]
    # CUPID = hex( AES-128-CBC-decrypt(ct, key, iv) ), no padding
    p = subprocess.run(
        f'printf {ct} | xxd -r -p | openssl enc -aes-128-cbc -d -K {key} -iv {iv} -nopad | xxd -p',
        shell=True, capture_output=True, text=True)
    return "CUPID=" + p.stdout.strip().replace("\n", "")

html = get(URL)
cookie = None
if "slowAES" in html:
    cookie = solve_cookie(html)
    html = get(URL + "?ckattempt=1", cookie=cookie)

# playlist entries: ['Label', 'mp3/rv-x/rv-x-NN.mp3']
pairs = re.findall(r"\['([^']+)',\s*'(mp3/[^']+\.mp3)'\]", html)
mp3s = sorted(set(m for _, m in pairs))
base = URL.rsplit("/", 1)[0] + "/"   # https://www.worldcomedu.com/media/
print(json.dumps({
    "url": URL, "cookie": cookie, "base": base,
    "n_pairs": len(pairs), "n_unique_mp3": len(mp3s),
    "playlist": pairs[:6], "all_mp3_sample": mp3s[:4] + (["..."] if len(mp3s) > 4 else []),
    "lesson_tracks": [m for m in mp3s if "full" not in m],
}, ensure_ascii=False, indent=2))
