#!/usr/bin/env python3
"""Write index.html from actions.json, so captions, zooms and click sounds follow the recording.
Run from video/demo after record.mjs: python3 scripts/build_index.py"""
import json
import subprocess

SPEED, CLIP_START = 1.2, 4.0
dur = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                     capture_output=True, text=True).stdout)
CLIP_LEN = round(dur("assets/clip.mp4"), 3)
CLIP_END = round(CLIP_START + CLIP_LEN, 3)
MONTAGE = [CLIP_END + 0.45 * i for i in range(9)]
CLOSE = round(CLIP_END + 0.45 * 8 + 0.9, 3)
TOTAL = round(CLOSE + 3.6, 3)
acts = json.load(open("actions.json"))
vt = lambda name, n=0: round(CLIP_START + [a for a in acts if a["name"] == name][n]["t"] / SPEED, 3)

CAPTIONS = [("roll", "Roll a seed"), ("city", "Choose a city"), ("theme", "Choose a curatorial theme"),
            ("forms", "Decide which art is allowed"), ("lineup", "Add rediscovered artists"),
            ("jargon", "Set the catalogue theory to Unbearable"), ("identity", "Pick a visual identity"),
            ("title", "Name your biennial"), ("scroll", "Every work has an installation view"),
            ("work-scroll", "and a wall label, a wall text and a footnoted essay"), ("surprise", "Or let it surprise you")]
caps = []
for i, (name, text) in enumerate(CAPTIONS):
    start = vt(name) - 0.1
    end = (vt(CAPTIONS[i + 1][0]) - 0.35) if i + 1 < len(CAPTIONS) else CLIP_END - 0.1
    if name == "work-scroll":
        end = vt("back") + 0.6
    caps.append((round(start, 3), round(end, 3), text))

ticks = [vt(a["name"], sum(1 for b in acts[:i] if b["name"] == a["name"])) for i, a in enumerate(acts)
         if a["name"] not in ("title", "scroll", "work-scroll", "end")]
typing_start = vt("title") + 0.12
z1 = (vt("title") - 0.15, vt("scroll") - 0.2)
z2 = (vt("work-scroll") - 0.1, vt("back") - 0.4)

import os
music_len = dur("audio/music/theme.wav") if os.path.exists("audio/music/theme.wav") else TOTAL
audio = [f'<audio id="music" src="audio/music/theme.wav" data-start="0" data-duration="{music_len:.3f}" data-track-index="30" data-volume="0.8"></audio>',
         f'<audio id="typing" src="audio/sfx/typing.wav" data-start="{typing_start:.3f}" data-duration="{dur("audio/sfx/typing.wav"):.3f}" data-track-index="20" data-volume="0.45"></audio>']
for i, t in enumerate(ticks):
    audio.append(f'<audio id="tick{i}" src="audio/sfx/tick.wav" data-start="{t:.3f}" data-duration="0.06" data-track-index="21" data-volume="0.55"></audio>')
for i, t in enumerate(MONTAGE[1:]):
    audio.append(f'<audio id="cut{i}" src="audio/sfx/tick.wav" data-start="{t:.3f}" data-duration="0.06" data-track-index="22" data-volume="0.35"></audio>')
audio.append(f'<audio id="chime" src="audio/sfx/chime.wav" data-start="{CLOSE:.3f}" data-duration="1.640" data-track-index="23" data-volume="0.7"></audio>')

caption_html = "\n".join(f'    <div class="cap" id="cap{i}">{t}</div>' for i, (_, _, t) in enumerate(caps))
caption_js = "\n".join(f'cap("#cap{i}", {a}, {b});' for i, (a, b, _) in enumerate(caps))
shots_html = "\n".join(f'    <div class="shot" id="m{i+1}" data-layout-allow-overflow><img src="assets/m{i+1}.jpg" alt=""></div>' for i in range(9))

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/SplitText.min.js"></script>
<style>
  :root {{ --ink: #141414; --paper: #ffffff; --muted: #9a9a95; --accent: #d4007a; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: var(--ink); font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; }}
  .serif {{ font-family: Georgia, "Times New Roman", serif; }}
  .beat {{ position: absolute; inset: 0; overflow: hidden; background: var(--ink); color: var(--paper); opacity: 0; }}
  #b1 {{ opacity: 1; }}
  .center {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }}
  .hook {{ font-size: 104px; line-height: 1.08; letter-spacing: -0.015em; max-width: 1500px; }}
  .sub {{ font-size: 64px; line-height: 1.15; max-width: 1400px; }}
  .brand {{ margin-top: 48px; font-size: 44px; color: var(--muted); }}
  .brand b {{ color: var(--paper); font-weight: 700; }}

  #clipwrap {{ position: absolute; inset: 0; transform-origin: 1800px 380px; }}
  #clip {{ position: absolute; inset: 0; width: 1920px; height: 1080px; }}
  #captions {{ position: absolute; right: 64px; bottom: 60px; width: 1100px; height: 80px; }}
  .cap {{ position: absolute; right: 0; bottom: 0; background: var(--ink); color: var(--paper); font-size: 38px; font-weight: 500;
          padding: 16px 26px; border-radius: 6px; white-space: nowrap; opacity: 0; }}

  .shot {{ position: absolute; inset: 0; opacity: 0; overflow: hidden; }}
  .shot img {{ width: 1920px; height: 1080px; object-fit: cover; display: block; }}
  .mcap {{ position: absolute; left: 64px; bottom: 60px; background: var(--ink); color: var(--paper); font-size: 38px; font-weight: 500;
           padding: 16px 26px; border-radius: 6px; opacity: 0; }}

  .wm {{ font-size: 150px; letter-spacing: -0.03em; line-height: 1; }}
  .wm b {{ font-weight: 700; }}
  .wm span {{ font-weight: 300; color: var(--muted); }}
  .tag {{ margin-top: 40px; font-size: 54px; }}
  .tiny {{ margin-top: 30px; font-size: 26px; color: var(--muted); }}
</style>
</head>
<body>
<div data-composition-id="studio-demo" data-width="1920" data-height="1080" data-start="0" data-duration="{TOTAL}"
     style="position:relative;width:100%;height:100%;">

  <div class="beat" id="b1"><div class="center" id="b1-c"><div class="hook serif" id="b1-h">Every biennale looks the same.</div></div></div>
  <div class="beat" id="b2"><div class="center" id="b2-c">
    <div class="sub serif" id="b2-h">So we built one you can curate.</div>
    <div class="brand" id="b2-b"><b>artgen</b> Studio</div>
  </div></div>

  <div id="clipwrap">
    <video id="clip" class="clip" src="assets/clip.mp4" data-start="{CLIP_START}" data-duration="{CLIP_LEN}" data-track-index="1" muted playsinline></video>
  </div>
  <div id="captions">
{caption_html}
  </div>

  <div class="beat" id="b4">
{shots_html}
    <div class="mcap" id="mcap1">76 kinds of work, drawn from 200 real ones</div>
    <div class="mcap" id="mcap2">One of them is a hole in the floor</div>
  </div>

  <div class="beat" id="b5"><div class="center" id="b5-c">
    <div class="wm" id="b5-wm"><b>artgen</b> <span>Studio</span></div>
    <div class="tag serif" id="b5-t">Curate a biennial that does not exist.</div>
    <div class="tiny" id="b5-s">Every artist, work, text and photograph is generated.</div>
  </div></div>

  {chr(10).join("  " + a for a in audio)}
</div>
<script>
gsap.registerPlugin(SplitText);
var tl = gsap.timeline({{ paused: true }});

// title cards and montage are opaque layers; the clip shows when they are hidden
tl.set("#b1", {{ opacity: 0 }}, 2.0);
tl.set("#b2", {{ opacity: 1 }}, 2.0);
tl.set("#b2", {{ opacity: 0 }}, {CLIP_START});
tl.set("#b4", {{ opacity: 1 }}, {CLIP_END});
tl.set("#b4", {{ opacity: 0 }}, {CLOSE});
tl.set("#b5", {{ opacity: 1 }}, {CLOSE});

// b1 hook
var s1 = SplitText.create("#b1-h", {{ type: "words" }});
tl.fromTo(s1.words, {{ opacity: 0, y: 28 }}, {{ opacity: 1, y: 0, duration: 0.5, stagger: 0.09, ease: "power3.out" }}, 0.15);
tl.fromTo("#b1-c", {{ scale: 1.0 }}, {{ scale: 1.04, duration: 2.0, ease: "power1.inOut" }}, 0);
// b2
tl.fromTo("#b2-h", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, 2.08);
tl.fromTo("#b2-b", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, 2.95);
tl.fromTo("#b2-c", {{ scale: 1.0 }}, {{ scale: 1.03, duration: 2.0, ease: "power1.inOut" }}, 2.0);

// clip: two zooms, on the typed title and on the work page
tl.fromTo("#clipwrap", {{ scale: 1.0 }}, {{ scale: 1.15, duration: 0.55, ease: "power2.inOut", immediateRender: false }}, {z1[0]:.3f});
tl.to("#clipwrap", {{ scale: 1.0, duration: 0.5, ease: "power2.inOut" }}, {z1[1]:.3f});
tl.set("#clipwrap", {{ transformOrigin: "1240px 640px" }}, {z1[1] + 0.55:.3f});
tl.to("#clipwrap", {{ scale: 1.25, duration: 0.55, ease: "power2.inOut" }}, {z2[0]:.3f});
tl.to("#clipwrap", {{ scale: 1.0, duration: 0.45, ease: "power2.inOut" }}, {z2[1]:.3f});

// captions
function cap(sel, a, b) {{
  tl.fromTo(sel, {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.22, ease: "power2.out" }}, a);
  tl.to(sel, {{ opacity: 0, duration: 0.15 }}, b);
}}
{caption_js}

// montage: hard cuts with a slow push on each photo
var M = {json.dumps([round(x, 3) for x in MONTAGE])};
M.forEach(function (t, i) {{
  var id = "#m" + (i + 1);
  var len = i === 8 ? 0.9 : 0.45;
  tl.set(id, {{ opacity: 1 }}, t);
  if (i < 8) tl.set(id, {{ opacity: 0 }}, t + len);
  tl.fromTo(id + " img", {{ scale: 1.0 }}, {{ scale: 1.05, duration: len, ease: "none" }}, t);
}});
tl.fromTo("#mcap1", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, M[0] + 0.1);
tl.set("#mcap1", {{ opacity: 0 }}, M[8]);
tl.fromTo("#mcap2", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, M[8] + 0.05);

// close
tl.fromTo("#b5-wm", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {CLOSE + 0.05:.3f});
tl.fromTo("#b5-t", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, {CLOSE + 0.75:.3f});
tl.fromTo("#b5-s", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {CLOSE + 1.3:.3f});
tl.to("#b5-c", {{ opacity: 0, duration: 0.4, ease: "power1.in" }}, {TOTAL - 0.4:.3f});

window.__timelines["studio-demo"] = tl;
</script>
</body>
</html>
"""
open("index.html", "w").write(html)
json.dump({"clip_start": CLIP_START, "clip_end": CLIP_END, "speed": SPEED, "montage": MONTAGE, "close": CLOSE, "total": TOTAL},
          open("timeline.json", "w"), indent=1)
print(f"index.html: clip {CLIP_START}-{CLIP_END}, montage {MONTAGE[0]:.2f}-{CLOSE}, total {TOTAL}; {len(caps)} captions, {len(ticks)} ticks")
