#!/usr/bin/env python3
"""Cut the recording and write timeline.json and index.html for the game video (1080x1080).
Inputs: config.json (address, play-along photographs), recording.json and raw/game.mp4 from record.mjs.
Run from video/game: python3 scripts/build_index.py"""
import html
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path("../..")
CONFIG = json.load(open("config.json"))
REC = json.load(open("recording.json"))
URL = CONFIG["url"]
FPS = 30


def dur(f):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


# ---- play-along: three photographs, each with a countdown and a stamp
MANIFEST = {e["id"]: e for e in json.load(open(ROOT / "game/real/manifest.json"))["entries"]}
LIBRARY = {e["id"]: e for e in json.load(open(ROOT / "library/index.json"))["entries"]}
ARCHETYPES = json.loads(subprocess.run(["python3", "-c", "import json; from artgen import corpus; "
                                        "print(json.dumps({a['id']: a['basis'] for a in corpus.archetypes()}))"],
                                       cwd=ROOT, capture_output=True, text=True, check=True).stdout)
Path("assets").mkdir(exist_ok=True)
photos = []
for i, p in enumerate(CONFIG["playalong"]):
    if p["kind"] == "real":
        e = MANIFEST[p["id"]]
        src = ROOT / "game/real" / f"{p['id']}.jpg"
        place = e["venue"] + (f", {e['year']}" if e["year"] else "")
        lines = [("who", e["artist"]), ("where", place), ("photo", e["credit"])]
    else:
        e = LIBRARY[p["id"]]
        src = ROOT / e["file"]
        lines = [("who", "AI made this room."), ("where", "It imitates " + " and ".join(ARCHETYPES[e["archetype"]][:2]) + ".")]
    shutil.copyfile(src, f"assets/p{i + 1}.jpg")
    photos.append({"kind": p["kind"], "lines": lines})

HOOK = 1.4            # the first photograph fills the frame with the question
SETTLE = 0.35         # then it moves into the frame of the play-along
GUESS, HOLD = 1.5, 1.3
beats, t = [], 0.0
for i in range(len(photos)):
    guess = HOOK + SETTLE if i == 0 else t + 0.15
    beats.append({"show": round(t, 3), "guess": round(guess, 3), "reveal": round(guess + GUESS, 3)})
    t = guess + GUESS + HOLD
ASK = round(t, 3)
CLIP_START = round(ASK + 1.1, 3)

# ---- the recording, cut into segments at their own speeds: (from action, offset, to action, offset, speed)
acts = {a["name"]: a["t"] for a in REC["actions"]}
SEGMENTS = [("answer0", -0.8, "label0", 0.0, 1.5),
            ("label0", 0.0, "next0", 0.15, 1.6),
            ("next0", 0.15, "answer1", -0.5, 2.6),
            ("answer1", -0.5, "next1", 0.15, 1.5),
            ("next1", 0.15, "next9", 0.25, 7.0),
            ("next9", 0.25, "end", 0.0, 1.3)]
segs, out_t = [], 0.0
for a, da, b, db, speed in SEGMENTS:
    t0, t1 = acts[a] + da, acts[b] + db
    frames = round((t1 - t0) / speed * FPS)
    segs.append({"from": t0, "to": t1, "speed": speed, "at": out_t, "frames": frames})
    out_t += frames / FPS


def vt(name, offset=0.0):
    """Video time of a recorded action."""
    t = acts[name] + offset
    s = next(s for s in segs if s["from"] <= t <= s["to"] + 1e-6)
    return round(CLIP_START + s["at"] + (t - s["from"]) / s["speed"], 3)


parts = [f"[0:v]trim=start={s['from']:.3f}:end={s['to']:.3f},setpts=(PTS-STARTPTS)/{s['speed']},fps={FPS},"
         f"trim=end_frame={s['frames']}[s{i}]" for i, s in enumerate(segs)]
graph = ";".join(parts) + ";" + "".join(f"[s{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=0,format=yuv420p[v]"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "raw/game.mp4", "-filter_complex", graph, "-map", "[v]", "-an",
                "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-g", "15", "-movflags", "+faststart", "assets/clip.mp4"], check=True)
CLIP_LEN = round(dur("assets/clip.mp4"), 3)
CLIP_END = round(CLIP_START + CLIP_LEN, 3)
POST = round(CLIP_END, 3)
CLOSE = round(POST + 2.7, 3)
TOTAL = round(CLOSE + 3.2, 3)

# ---- captions over the recording
second = "AI copies real works. The label names them." if not REC["real"][1] else "A real room gets its artist and venue."
CAPTIONS = [(vt("answer0", -0.8), vt("label0", -0.2), "Tap Real or AI"),
            (vt("label0", -0.2), vt("next0", 0.1), "The wall label tells you the truth"),
            (vt("answer1", -0.4), vt("next1", 0.1), second),
            (vt("next1", 0.15), vt("next9", 0.2), "Ten photographs a day"),
            (vt("next9", 0.3), vt("post", -0.25), "Everyone gets the same ten"),
            (vt("post", -0.25), CLIP_END, "Then post your score")]
taps = [vt(a["name"]) for a in REC["actions"] if a["name"].startswith(("answer", "next", "post"))]

# ---- the post: the text that the page put in its "Post on X" link
share_lines = REC["share"].split("\n")
score = int(share_lines[1].split()[1].split("/")[0])
shutil.copyfile(ROOT / f"artgen/studio_static/share/{score}.jpg", "assets/card.jpg")
shutil.copyfile(ROOT / "artgen/studio_static/icon.svg", "assets/icon.svg")
squares = [c for c in share_lines[1].split(" ")[0]]
post_html = (f'<p class="pl">{html.escape(share_lines[0])}</p>'
             f'<p class="pl grid">{"".join(f"<span class=sq>{c}</span>" for c in squares)} {html.escape(share_lines[1].split(" ", 1)[1])}</p>'
             f'<p class="pl link">{html.escape(share_lines[2])}</p>')

# ---- sound: music, a tick for each tap and count, a stamp for each reveal, a chime on the close
audio = [f'<audio id="music" src="audio/music/theme.wav" data-start="0" data-duration="{TOTAL:.3f}" data-track-index="30" data-volume="0.8"></audio>']
n = 0


def sfx(src, at, length, vol, track):
    global n
    n += 1
    audio.append(f'<audio id="fx{n}" src="audio/sfx/{src}.wav" data-start="{at:.3f}" data-duration="{length}" data-track-index="{track}" data-volume="{vol}"></audio>')


for b in beats:
    for k in range(3):
        sfx("tick", b["guess"] + 0.5 * k, 0.06, 0.5, 20)
    sfx("stamp", b["reveal"], 0.5, 0.9, 21)
for tt in taps:
    sfx("tick", tt, 0.06, 0.4, 22)
sfx("pop", POST + 0.15, 0.18, 0.7, 23)
sfx("chime", CLOSE, 1.6, 0.6, 23)

# ---- html
def play_layer(i, p):
    stamp = ('<div class="stamp real">Real</div>' if p["kind"] == "real"
             else '<div class="stamp ai">AI</div>')
    lines = "".join(f'<p class="{c}">{html.escape(t)}</p>' for c, t in p["lines"])
    return f"""
  <div class="beat pa{' first' if i == 0 else ''}" id="pa{i}">
    <div class="head"><span class="count">{i + 1} of {len(photos)}</span><h1 class="serif">Real or AI?</h1>
      <div class="clock" id="clock{i}"><span>3</span><span>2</span><span>1</span></div></div>
    <div class="frame" id="frame{i}"><img src="assets/p{i + 1}.jpg" alt="">{stamp}</div>
    <div class="bar" id="bar{i}"></div>
    <div class="foot">
      <div class="choices" id="choices{i}"><div class="choice">Real</div><div class="choice">AI</div></div>
      <div class="credit {p['kind']}" id="credit{i}">{lines}</div>
    </div>
  </div>"""


layers = "".join(play_layer(i, p) for i, p in enumerate(photos))
caption_html = "\n".join(f'    <div class="cap" id="cap{i}">{html.escape(t)}</div>' for i, (_, _, t) in enumerate(CAPTIONS))

js_beats = json.dumps(beats)
js_caps = json.dumps([[a, b] for a, b, _ in CAPTIONS])
page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400;500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=block">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
  :root {{ --ink: #141414; --ground: #ffffff; --soft: #f4f4f1; --muted: #626260; --rule: #e1e1dd; --right: #1f7a4d; --wrong: #a4281f; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ width: 1080px; height: 1080px; overflow: hidden; background: var(--ground); color: var(--ink);
    font-family: "Schibsted Grotesk", "Helvetica Neue", Arial, sans-serif; }}
  .serif {{ font-family: "Newsreader", Georgia, serif; font-weight: 400; }}
  .beat {{ position: absolute; inset: 0; overflow: hidden; background: var(--ground); opacity: 0; }}

  /* play-along */
  .pa .head {{ position: absolute; left: 60px; right: 60px; top: 44px; height: 140px; }}
  .pa .count {{ display: block; font-size: 30px; font-weight: 500; color: var(--muted); font-variant-numeric: tabular-nums; }}
  .pa h1 {{ font-size: 100px; line-height: 1; letter-spacing: -0.01em; margin-top: 6px; }}
  .clock {{ position: absolute; right: 0; top: 18px; width: 116px; height: 116px; border: 4px solid var(--ink); border-radius: 50%; }}
  .clock span {{ position: absolute; inset: 0; display: grid; place-items: center; font-size: 64px; font-weight: 600; opacity: 0; font-variant-numeric: tabular-nums; }}
  .frame {{ position: absolute; left: 60px; top: 200px; width: 960px; height: 640px; overflow: hidden; background: var(--soft);
    box-shadow: 0 2px 4px rgba(20,20,20,.14), 0 24px 40px -22px rgba(20,20,20,.45); }}
  .frame img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
  .bar {{ position: absolute; left: 60px; top: 858px; width: 960px; height: 8px; background: var(--ink); transform-origin: left center; transform: scaleX(0); }}
  .foot {{ position: absolute; left: 60px; right: 60px; top: 884px; height: 176px; }}
  .choices {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  .choice {{ height: 120px; border: 3px solid var(--ink); border-radius: 6px; display: grid; place-items: center; font-size: 54px; font-weight: 600; }}
  .credit {{ position: absolute; inset: 0; opacity: 0; }}
  .credit .who {{ font-size: 50px; font-weight: 600; line-height: 1.1; }}
  .credit .where {{ font-size: 36px; line-height: 1.22; margin-top: 8px; }}
  .credit .photo {{ font-size: 24px; color: var(--muted); margin-top: 8px; }}
  .credit.real .who {{ color: var(--right); }}
  .credit.ai .who {{ color: var(--wrong); }}
  .credit.ai .where {{ color: var(--ink); }}
  .stamp {{ position: absolute; left: 50%; top: 50%; padding: 18px 48px 14px; border: 12px solid currentColor; border-radius: 14px;
    background: rgba(255,255,255,.92); font-size: 150px; font-weight: 700; line-height: 1; text-transform: uppercase; letter-spacing: .04em;
    text-align: center; opacity: 0; }}
  .stamp small {{ display: block; font-size: 34px; letter-spacing: .02em; text-transform: none; font-weight: 600; margin-top: 4px; }}
  .stamp.real {{ color: var(--right); }}
  .stamp.ai {{ color: var(--wrong); }}

  /* the first photograph starts full-bleed under the question */
  #pa0 {{ opacity: 1; }}
  #pa0 .head, #pa0 .bar, #pa0 .foot {{ opacity: 0; }}
  #hook {{ position: absolute; left: 0; right: 0; top: 0; padding: 70px 60px 160px;
    background: linear-gradient(rgba(10,10,10,.62), rgba(10,10,10,.35) 60%, rgba(10,10,10,0)); color: #fff; }}
  #hook h1 {{ font-size: 132px; line-height: .98; letter-spacing: -0.015em; }}
  #brand {{ position: absolute; left: 40px; bottom: 40px; display: flex; align-items: center; gap: 14px; padding: 12px 24px 12px 12px;
    background: #fff; border-radius: 10px; box-shadow: 0 10px 30px -12px rgba(0,0,0,.5); }}
  #brand img {{ width: 60px; height: 60px; display: block; }}
  #brand span {{ font-size: 36px; font-weight: 700; letter-spacing: -0.01em; }}

  /* the card between the play-along and the recording */
  .center {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 0 80px; }}
  #ask h2 {{ font-size: 112px; line-height: 1.02; letter-spacing: -0.01em; }}
  #ask p {{ font-size: 44px; font-weight: 500; margin-top: 34px; color: var(--muted); }}

  /* the recording */
  #clipwrap {{ position: absolute; inset: 0; }}
  #clip {{ position: absolute; inset: 0; width: 1080px; height: 1080px; }}
  #captions {{ position: absolute; left: 0; right: 0; top: 36px; height: 100px; }}
  .cap {{ position: absolute; left: 50%; top: 0; transform: translateX(-50%); background: var(--ink); color: #fff; font-size: 44px; font-weight: 600;
    padding: 18px 32px; border-radius: 10px; white-space: nowrap; opacity: 0; box-shadow: 0 10px 30px -12px rgba(0,0,0,.5); }}

  /* the post */
  #post h2 {{ position: absolute; left: 0; right: 0; top: 96px; text-align: center; font-size: 84px; line-height: 1; }}
  .card {{ position: absolute; left: 90px; right: 90px; top: 236px; border: 2px solid var(--rule); border-radius: 22px; padding: 40px 44px 44px;
    background: #fff; box-shadow: 0 30px 60px -36px rgba(20,20,20,.45); }}
  .pl {{ font-size: 42px; line-height: 1.3; }}
  .pl.grid {{ font-size: 42px; margin-top: 4px; white-space: nowrap; }}
  .sq {{ display: inline-block; font-size: 44px; }}
  .pl.link {{ font-size: 34px; color: var(--muted); margin-top: 4px; }}
  .card img {{ display: block; width: 100%; margin-top: 26px; border-radius: 14px; border: 2px solid var(--rule); }}

  /* close */
  #close .icon {{ width: 150px; height: 150px; margin-bottom: 44px; }}
  #close h2 {{ font-size: 140px; line-height: 1; letter-spacing: -0.015em; }}
  #close .tag {{ font-size: 54px; font-weight: 500; margin-top: 30px; }}
  #close .url {{ font-size: 36px; font-weight: 600; white-space: nowrap; margin-top: 64px; padding: 20px 34px; border: 3px solid var(--ink); border-radius: 10px; }}
</style>
</head>
<body>
<div data-composition-id="game-video" data-width="1080" data-height="1080" data-start="0" data-duration="{TOTAL}"
     style="position:relative;width:100%;height:100%;">

  <div id="clipwrap">
    <video id="clip" class="clip" src="assets/clip.mp4" data-start="{CLIP_START}" data-duration="{CLIP_LEN}" data-track-index="1" muted playsinline></video>
  </div>
  <div id="captions">
{caption_html}
  </div>
{layers}
  <div id="hook"><h1 class="serif">Is this room real?</h1></div>
  <div id="brand"><img src="assets/icon.svg" alt=""><span>Art or Artifice?</span></div>

  <div class="beat" id="ask"><div class="center">
    <h2 class="serif">How many did you get?</h2>
    <p>Play ten a day.</p>
  </div></div>

  <div class="beat" id="post">
    <h2 class="serif">Post your score</h2>
    <div class="card" id="card">{post_html}<img src="assets/card.jpg" alt=""></div>
  </div>

  <div class="beat" id="close"><div class="center">
    <img class="icon" src="assets/icon.svg" alt="">
    <h2 class="serif">Art or Artifice?</h2>
    <div class="tag">A new round every day</div>
    <div class="url">{html.escape(URL)}</div>
  </div></div>

  {chr(10).join("  " + a for a in audio)}
</div>
<script>
gsap.set(".stamp", {{ xPercent: -50, yPercent: -50, rotation: -7 }});
var tl = gsap.timeline({{ paused: true }});
var B = {js_beats};

// hook: the first photograph and the question are there from the first frame
tl.fromTo("#frame0 img", {{ scale: 1.06 }}, {{ scale: 1.0, duration: {HOOK + SETTLE}, ease: "power1.out" }}, 0);
tl.fromTo("#hook h1", {{ y: 8 }}, {{ y: 0, duration: 0.6, ease: "power2.out" }}, 0);
tl.to("#hook, #brand", {{ opacity: 0, duration: 0.2 }}, {HOOK - 0.05});
// the frame sits in its play-along place; scaled 1.6875x (1620x1080) it covers the square
tl.fromTo("#frame0", {{ scale: 1.6875, y: 20 }}, {{ scale: 1, y: 0, duration: {SETTLE}, ease: "power3.inOut", immediateRender: true }}, {HOOK});
tl.to("#pa0 .head, #pa0 .bar, #pa0 .foot", {{ opacity: 1, duration: 0.25 }}, {HOOK + 0.12});

B.forEach(function (b, i) {{
  var p = "#pa" + i;
  if (i > 0) {{
    tl.set(p, {{ opacity: 1 }}, b.show);
    tl.set("#pa" + (i - 1), {{ opacity: 0 }}, b.show);
    tl.fromTo("#frame" + i, {{ scale: 0.97, opacity: 0.4 }}, {{ scale: 1, opacity: 1, duration: 0.25, ease: "power2.out" }}, b.show);
  }}
  // countdown: 3, 2, 1 and a draining bar
  var nums = document.querySelectorAll("#clock" + i + " span");
  for (var k = 0; k < 3; k++) {{
    tl.fromTo(nums[k], {{ opacity: 0, scale: 1.3 }}, {{ opacity: 1, scale: 1, duration: 0.15, ease: "power2.out" }}, b.guess + 0.5 * k);
    tl.set(nums[k], {{ opacity: 0 }}, b.guess + 0.5 * (k + 1));
  }}
  tl.fromTo("#bar" + i, {{ scaleX: 1 }}, {{ scaleX: 0, duration: b.reveal - b.guess, ease: "none" }}, b.guess);
  // reveal: the stamp lands, the credit replaces the choices
  tl.fromTo(p + " .stamp", {{ opacity: 0, scale: 1.7 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power4.in" }}, b.reveal - 0.12);
  tl.fromTo("#frame" + i, {{ x: 0 }}, {{ x: 6, duration: 0.05, yoyo: true, repeat: 3, ease: "none" }}, b.reveal + 0.08);
  tl.to("#clock" + i, {{ opacity: 0, duration: 0.15 }}, b.reveal);
  tl.to("#choices" + i, {{ opacity: 0, duration: 0.15 }}, b.reveal);
  tl.fromTo("#credit" + i, {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }}, b.reveal + 0.1);
}});

tl.set("#pa{len(photos) - 1}", {{ opacity: 0 }}, {ASK});
tl.set("#ask", {{ opacity: 1 }}, {ASK});
tl.fromTo("#ask h2", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {ASK});
tl.fromTo("#ask p", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {ASK + 0.35});
tl.set("#ask", {{ opacity: 0 }}, {CLIP_START});

// captions over the recording
{js_caps}.forEach(function (c, i) {{
  tl.fromTo("#cap" + i, {{ opacity: 0, y: -10 }}, {{ opacity: 1, y: 0, duration: 0.2, ease: "power2.out" }}, c[0]);
  tl.to("#cap" + i, {{ opacity: 0, duration: 0.12 }}, c[1] - 0.12);
}});

// the post
tl.set("#post", {{ opacity: 1 }}, {POST});
tl.fromTo("#post h2", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }}, {POST});
tl.fromTo("#card", {{ opacity: 0, y: 60 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {POST + 0.1});
tl.fromTo("#card .sq", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.18, stagger: 0.05, ease: "back.out(2)" }}, {POST + 0.35});

// close
tl.set("#close", {{ opacity: 1 }}, {CLOSE});
tl.set("#post", {{ opacity: 0 }}, {CLOSE});
tl.fromTo("#close .icon", {{ opacity: 0, scale: 0.85 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(1.6)" }}, {CLOSE});
tl.fromTo("#close h2", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, {CLOSE + 0.1});
tl.fromTo("#close .tag", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {CLOSE + 0.5});
tl.fromTo("#close .url", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {CLOSE + 0.9});

window.__timelines["game-video"] = tl;
</script>
</body>
</html>
"""
open("index.html", "w").write(page)
json.dump({"url": URL, "beats": beats, "ask": ASK, "clip_start": CLIP_START, "clip_end": CLIP_END, "segments": segs,
           "captions": CAPTIONS, "taps": taps, "post": POST, "close": CLOSE, "total": TOTAL},
          open("timeline.json", "w"), indent=1)
print(f"index.html: play-along 0-{ASK}, clip {CLIP_START}-{CLIP_END}, post {POST}, close {CLOSE}, total {TOTAL}")
