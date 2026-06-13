#!/usr/bin/env python3
"""Generate a book's offline HTML reader from {dir}/spec.json (English UI).
Grouped BY UNIT. Hamburger menu lists units; the header shows the unit currently
in view. Each lesson shows Word List + Reading pages with 'Listen' buttons that
feed ONE sticky bottom player (prev/next/seek/speed/close, auto-advance), readable
on tablets. Plus a show/hide top-bar toggle.
Usage: gen_html.py <book-dir> "<title>"
"""
import sys, json, html as _html
from pathlib import Path

bdir = Path(sys.argv[1]); title = sys.argv[2]
spec = json.loads((bdir / "spec.json").read_text())

def page_file(pn):
    return f"pages/{next((bdir/'pages').glob(f'p{pn:03d}.*')).name}"
def esc(s): return _html.escape(str(s), quote=True)

units = []
for L in spec:
    if not units or units[-1][0] != L["unit"]:
        units.append((L["unit"], []))
    units[-1][1].append(L)

menu, body = [], []
for ui, (uname, lessons) in enumerate(units, 1):
    uid = f"unit-{ui}"
    menu.append(f'<a href="#{uid}">Unit {ui} · {esc(uname)}</a>')
    lh = []
    for L in lessons:
        blocks = []
        for it in L["items"]:
            kind = it["type"]
            imgs = "".join(f'<img loading="lazy" src="{page_file(p)}" alt="page {p}">' for p in it["pages"])
            btn = ""
            if it.get("mp3"):
                btn = (f'<button class="nghe" data-src="audio/{esc(it["mp3"])}" '
                       f'data-unit="Unit {ui} · {esc(uname)}" '
                       f'data-title="Lesson {L["lesson"]} · {esc(L["title"])} — {kind}">'
                       f'▶ Listen — {kind}</button>')
            blocks.append(f'<div class="block"><div class="btag">{kind}</div>{btn}'
                          f'<div class="imgs">{imgs}</div></div>')
        lh.append(f'<div class="lesson"><h3>Lesson {L["lesson"]} — {esc(L["title"])}</h3>'
                  + "".join(blocks) + "</div>")
    body.append(f'<section id="{uid}" class="unit" data-unit="Unit {ui} · {esc(uname)}">'
                f'<h2 class="unit-h"><span class="unum">UNIT {ui}</span>{esc(uname)}</h2>'
                + "".join(lh) + "</section>")

CSS = """
  :root{--accent:#1f6fb2;--bg:#f4f6f8;--card:#fff;--bar:#1e2a3a;--red:#ef4444}
  *{box-sizing:border-box}
  html{scroll-behavior:smooth;scroll-padding-top:64px}
  body{margin:0;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:var(--bg);color:#222}
  header.top{position:sticky;top:0;z-index:30;background:#fff;border-bottom:2px solid var(--accent);box-shadow:0 2px 6px rgba(0,0,0,.08)}
  header.top.hidden{display:none}
  .bar{display:flex;align-items:center;gap:12px;padding:10px 14px}
  .burger{border:none;background:var(--accent);color:#fff;width:40px;height:40px;border-radius:10px;font-size:19px;cursor:pointer;flex:none}
  .htxt{min-width:0}
  .htxt .bk{font-size:12px;color:#7c8a99;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .htxt .cur{font-size:17px;font-weight:800;color:var(--accent);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .menu{display:none;border-top:1px solid #eef1f4;max-height:60vh;overflow:auto;background:#fff;padding:6px}
  .menu.open{display:block}
  .menu a{display:block;padding:11px 14px;border-radius:8px;text-decoration:none;color:#243;font-weight:600;font-size:15px}
  .menu a:hover,.menu a.active{background:var(--accent);color:#fff}
  #barToggle{position:fixed;top:8px;right:10px;z-index:40;border:none;background:var(--accent);color:#fff;width:32px;height:32px;border-radius:50%;font-size:14px;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,.25);opacity:.85}
  main{max-width:900px;margin:0 auto;padding:18px 14px 140px}
  .unit{margin-bottom:40px}
  .unit-h{font-size:22px;color:var(--accent);background:#eaf2fa;border-radius:10px;padding:12px 16px;margin:0 0 16px}
  .unit-h .unum{display:inline-block;font-size:13px;font-weight:800;letter-spacing:.08em;background:var(--accent);color:#fff;padding:2px 10px;border-radius:8px;margin-right:10px;vertical-align:middle}
  .lesson{margin:0 0 24px}
  .lesson h3{font-size:18px;border-left:5px solid var(--accent);padding:5px 0 5px 12px;margin:0 0 12px}
  .block{background:var(--card);border-radius:12px;padding:14px;margin:12px 0;box-shadow:0 1px 4px rgba(0,0,0,.07)}
  .btag{display:inline-block;font-size:12px;font-weight:700;color:#fff;background:var(--accent);padding:3px 12px;border-radius:10px;margin-bottom:10px}
  button.nghe{display:inline-flex;align-items:center;gap:8px;font-size:15px;font-weight:700;color:#fff;background:var(--accent);border:none;border-radius:10px;padding:10px 18px;margin-bottom:12px;cursor:pointer}
  button.nghe:hover{filter:brightness(1.08)}
  button.nghe.playing{background:var(--red)}
  .imgs img{width:100%;height:auto;display:block;border-radius:8px;margin:8px 0;border:1px solid #e6ebf0}
  /* bottom player */
  #player{position:fixed;left:0;right:0;bottom:0;z-index:35;background:var(--bar);color:#fff;display:none;
    padding:10px 16px;border-top:3px solid var(--red);box-shadow:0 -2px 12px rgba(0,0,0,.3)}
  #player.show{display:block}
  #player .ptop{display:flex;align-items:center;gap:14px}
  #player .pinfo{flex:1;min-width:0}
  #player .punit{color:var(--red);font-size:11px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  #player .ptitle{font-size:16px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  #player .pctrl{display:flex;align-items:center;gap:16px;flex:none}
  #player .pctrl button{background:none;border:none;color:#fff;font-size:20px;cursor:pointer;line-height:1}
  #player .pplay{width:48px;height:48px;border-radius:50%;background:var(--red)!important;font-size:21px;display:flex;align-items:center;justify-content:center}
  #player .pright{display:flex;align-items:center;gap:8px;flex:none}
  #player .pright button{background:#33425a;border:none;color:#fff;border-radius:8px;padding:7px 11px;font-size:13px;cursor:pointer}
  #player .pseek{display:flex;align-items:center;gap:10px;font-size:12px;color:#aebacb;margin-top:8px}
  #player .pseek input{flex:1;accent-color:var(--red)}
  @media(max-width:820px){
    #player .ptop{flex-wrap:wrap}
    #player .pinfo{flex:1 0 100%;order:-1;margin-bottom:6px}
    #player .ptitle{font-size:17px;white-space:normal}
    #player .pctrl{flex:1;justify-content:center}
  }
"""

JS = """
  var au=new Audio(), btns=[].slice.call(document.querySelectorAll('button.nghe')),
      P=document.getElementById('player'), cur=-1, speeds=[1,1.25,1.5,0.75], si=0;
  var elPlay=P.querySelector('.pplay'),elUnit=P.querySelector('.punit'),elTitle=P.querySelector('.ptitle'),
      elCur=P.querySelector('.cur2'),elRem=P.querySelector('.rem'),elSeek=P.querySelector('.pseek input'),
      elSpeed=P.querySelector('.pspeed');
  function fmt(t){t=Math.max(0,t|0);return (t/60|0)+':'+('0'+(t%60)).slice(-2);}
  function mark(){btns.forEach(function(b,i){b.classList.toggle('playing',i===cur&&!au.paused);});
    elPlay.textContent=au.paused?'▶':'⏸';}
  function load(i){if(i<0||i>=btns.length)return;cur=i;var b=btns[i];
    au.src=b.dataset.src;au.playbackRate=speeds[si];
    elUnit.textContent=b.dataset.unit;elTitle.textContent=b.dataset.title;
    P.classList.add('show');au.play();}
  btns.forEach(function(b,i){b.addEventListener('click',function(){i===cur?(au.paused?au.play():au.pause()):load(i);});});
  elPlay.onclick=function(){au.paused?au.play():au.pause();};
  P.querySelector('.pprev').onclick=function(){load(cur-1);};
  P.querySelector('.pnext').onclick=function(){load(cur+1);};
  P.querySelector('.pclose').onclick=function(){au.pause();P.classList.remove('show');cur=-1;mark();};
  elSpeed.onclick=function(){si=(si+1)%speeds.length;au.playbackRate=speeds[si];elSpeed.textContent=speeds[si]+'x';};
  P.querySelector('.plist').onclick=function(){if(cur>=0)btns[cur].scrollIntoView({block:'center'});};
  au.addEventListener('play',mark);au.addEventListener('pause',mark);
  au.addEventListener('ended',function(){if(cur+1<btns.length)load(cur+1);else mark();});
  au.addEventListener('timeupdate',function(){if(au.duration){elSeek.value=au.currentTime/au.duration*100;
    elCur.textContent=fmt(au.currentTime);elRem.textContent='-'+fmt(au.duration-au.currentTime);}});
  elSeek.addEventListener('input',function(){if(au.duration)au.currentTime=elSeek.value/100*au.duration;});
  // hamburger menu
  var mb=document.getElementById('menuBtn'), menu=document.getElementById('menu');
  mb.onclick=function(){menu.classList.toggle('open');};
  menu.querySelectorAll('a').forEach(function(a){a.onclick=function(){menu.classList.remove('open');};});
  // current-unit indicator (topmost unit in view) + active menu item
  var curEl=document.getElementById('curUnit'), mlinks=[].slice.call(menu.querySelectorAll('a')),
      sections=[].slice.call(document.querySelectorAll('section.unit'));
  function onScroll(){var y=80,best=sections[0];
    for(var i=0;i<sections.length;i++){if(sections[i].getBoundingClientRect().top<=y)best=sections[i];}
    if(best){curEl.textContent=best.dataset.unit;
      var id=best.id;mlinks.forEach(function(a){a.classList.toggle('active',a.getAttribute('href')==='#'+id);});}}
  window.addEventListener('scroll',onScroll,{passive:true});window.addEventListener('load',onScroll);onScroll();
  // show/hide top bar
  var hdr=document.querySelector('header.top'),tg=document.getElementById('barToggle');
  function pad(){document.documentElement.style.scrollPaddingTop=
    (hdr.classList.contains('hidden')?52:hdr.querySelector('.bar').offsetHeight+10)+'px';}
  tg.onclick=function(){hdr.classList.toggle('hidden');
    tg.textContent=hdr.classList.contains('hidden')?'▼':'▲';pad();};
  window.addEventListener('resize',pad);window.addEventListener('load',pad);pad();
"""

PLAYER = """<div id="player">
  <div class="ptop">
    <div class="pinfo"><div class="punit"></div><div class="ptitle"></div></div>
    <div class="pctrl"><button class="pprev" title="Previous">⏮</button>
      <button class="pplay" title="Play/Pause">▶</button>
      <button class="pnext" title="Next">⏭</button></div>
    <div class="pright"><button class="pspeed">1x</button>
      <button class="plist" title="Go to current">☰</button>
      <button class="pclose" title="Close">✕</button></div>
  </div>
  <div class="pseek"><span class="cur2">0:00</span><input type="range" min="0" max="100" value="0"><span class="rem">0:00</span></div>
</div>"""

doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<style>{CSS}</style></head>
<body>
<button id="barToggle" title="Hide/show top bar">▲</button>
<header class="top">
  <div class="bar">
    <button id="menuBtn" class="burger" title="Menu">☰</button>
    <div class="htxt"><div class="bk"><a href="../index.html" style="color:inherit;text-decoration:none">← {esc(title)}</a></div>
      <div class="cur" id="curUnit"></div></div>
  </div>
  <nav id="menu" class="menu">{''.join(menu)}</nav>
</header>
<main>{''.join(body)}</main>
{PLAYER}
<script>{JS}</script>
</body></html>"""
(bdir / "index.html").write_text(doc, encoding="utf-8")
print(f"{bdir.name}: wrote index.html ({len(units)} units, {len(spec)} lessons)")
