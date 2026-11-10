#!/usr/bin/env python3
"""Music bed for the game video, composed to timeline.json. Deterministic, no samples, standard library only.
A count of three notes before each answer, a chord on each stamp (major for a real room, darker for an AI room),
a quiet arpeggio under the recording, and a resolve on the close.
Run from video/game after build_index.py: python3 scripts/make-music.py"""
import array
import json
import math
import os
import subprocess
import wave

TL = json.load(open("timeline.json"))
CONFIG = json.load(open("config.json"))
SR = 44100
TOTAL = TL["total"]
out = array.array("d", bytes(8 * (int(TOTAL * SR) + SR)))
TAU = 2 * math.pi


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def note(t0, m, dur, vel=0.5, bright=1.0):
    f, s = midi(m), int(t0 * SR)
    n = min(int(dur * SR), len(out) - s)
    decay, w = dur * 0.35, TAU * f / SR
    for i in range(n):
        t = i / SR
        env = math.exp(-t / decay) * (1 - math.exp(-t / 0.006))
        x = w * i
        out[s + i] += vel * env * (math.sin(x) + 0.35 * bright * math.sin(2 * x + 0.3) + 0.12 * bright * math.sin(3 * x + 0.7)
                                   + 0.25 * math.sin(1.003 * x))


def chord(t0, notes, dur, vel=0.3, spread=0.012, bright=1.0):
    for i, m in enumerate(notes):
        note(t0 + i * spread, m, dur, vel, bright)


def drone(t0, t1, notes, vel):
    s, e = int(t0 * SR), int(t1 * SR)
    for m in notes:
        w = TAU * midi(m) / SR
        for i in range(s, e):
            k = (i - s) / (e - s)
            out[i] += vel * math.sin(w * i) * min(1, k / 0.15) * min(1, (1 - k) / 0.1)


A2, C3, D3, E3, F2, G2 = 45, 48, 50, 52, 41, 43
A3, C4, D4, E4, F4, G4, A4, B4 = 57, 60, 62, 64, 65, 67, 69, 71
C5, D5, E5, G5, A5, C6 = 72, 74, 76, 79, 81, 84

# hook: a low drone and one high note under the question
drone(0, TL["beats"][0]["guess"], [A2, E3], 0.07)
note(0.0, E5, 1.4, vel=0.16)

# play-along: three counting notes, then a chord on the stamp
for b, p in zip(TL["beats"], CONFIG["playalong"]):
    for k, m in enumerate([A4, C5, E5]):
        note(b["guess"] + 0.5 * k, m, 0.45, vel=0.11)
    if p["kind"] == "real":
        chord(b["reveal"], [C3, E4, G4, D5], 1.3, vel=0.22)
    else:
        chord(b["reveal"], [F2, A3, E4, F4], 1.3, vel=0.22, bright=0.7)

# the question card
chord(TL["ask"], [D3, A3, E4, A4], 1.2, vel=0.2, bright=0.8)

# recording: a quiet arpeggio, chord changes every 2.4 s
prog = [[A2, E4, A4, C5], [F2, C4, F4, A4], [C3, E4, G4, C5], [G2, D4, G4, B4]]
t, k = TL["clip_start"], 0
while t < TL["post"] - 0.2:
    ch = prog[k % 4]
    note(t, ch[0], 2.4, vel=0.14, bright=0.6)
    for j in range(8):
        tt = t + 0.3 * j
        if tt < TL["post"] - 0.2:
            note(tt, ch[1:][j % 3], 0.6, vel=0.06, bright=0.9)
    t += 2.4
    k += 1

# the post: two rising notes; close: resolve and a last note
note(TL["post"] + 0.1, G5, 0.6, vel=0.12)
note(TL["post"] + 0.3, C6, 1.0, vel=0.12)
chord(TL["post"] + 0.1, [C3, G4, C5], 2.4, vel=0.16, bright=0.7)
chord(TL["close"], [A2, C4, E4, B4], 3.4, vel=0.24, bright=0.85)
note(TL["close"] + 0.9, E5, 2.2, vel=0.14)
note(TL["close"] + 1.1, C5, 2.0, vel=0.1)

# one-pole low-pass for a felt-piano softness, then peak-normalise
y, a = 0.0, 0.18
for i in range(len(out)):
    y += a * (out[i] - y)
    out[i] = 0.75 * y + 0.25 * out[i]
n = int(TOTAL * SR)
peak = max(abs(v) for v in out[:n]) or 1.0
pcm = array.array("h", (int(v / peak * 0.6 * 32767) for v in out))
os.makedirs("audio/music", exist_ok=True)
with wave.open("audio/music/theme_raw.wav", "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
# loudnorm shifts its output timestamps; asetpts resets them, so the trim gives exactly TOTAL seconds
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "audio/music/theme_raw.wav",
                "-af", f"aecho=0.7:0.35:38|71:0.22|0.14,loudnorm=I=-20:TP=-3:LRA=9,aresample=48000,asetpts=N/SR/TB,"
                       f"atrim=end={TOTAL},afade=t=out:st={TOTAL - 1.0}:d=1.0", "audio/music/theme.wav"], check=True)
os.remove("audio/music/theme_raw.wav")
print("theme.wav", subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "audio/music/theme.wav"],
                                  capture_output=True, text=True).stdout.strip())
