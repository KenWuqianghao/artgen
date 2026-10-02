#!/usr/bin/env python3
"""Music bed for the Studio demo, composed to the beat map in STORYBOARD.md. Deterministic, no samples.
A minor / C major, felt-piano-ish additive tone. Run from video/demo: python3 scripts/make-music.py"""
import json, math, os, subprocess, wave
import numpy as np

TL = json.load(open("timeline.json"))
SR = 48000; TOTAL = TL["total"]
out = np.zeros(int(TOTAL * SR) + SR)
def midi(n): return 440.0 * 2 ** ((n - 69) / 12)
def note(t0, m, dur, vel=0.5, bright=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR; f = midi(m)
    env = np.exp(-t / (dur * 0.35)) * (1 - np.exp(-t / 0.006))
    sig = (np.sin(2*math.pi*f*t) + 0.35*bright*np.sin(2*math.pi*2*f*t + 0.3) + 0.12*bright*np.sin(2*math.pi*3*f*t + 0.7)
           + 0.05*np.sin(2*math.pi*4*f*t) + 0.25*np.sin(2*math.pi*f*1.003*t))
    s = int(t0 * SR); e = min(len(out), s + n)
    out[s:e] += (sig * env * vel)[:e - s]
def chord(t0, notes, dur, vel=0.4, spread=0.015, bright=1.0):
    for i, m in enumerate(notes): note(t0 + i*spread, m, dur, vel, bright)

A2, B2, C3, D3, E3, F2, G2 = 45, 47, 48, 50, 52, 41, 43
C4, D4, E4, F4, G4, A4, B4, C5, D5, E5, G5, A5, C6 = 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 79, 81, 84

# hook: drone with a rubbed second, hard stop at 2.0
n = int(2.0 * SR); t = np.arange(n) / SR
d = 0.22*np.sin(2*math.pi*midi(A2)*t) + 0.12*np.sin(2*math.pi*midi(B2)*t) + 0.08*np.sin(2*math.pi*midi(A2-12)*t)
out[:n] += d * np.minimum(1, t/0.15) * (0.6 + 0.4*t/2.0)
# answer: Cmaj7, high note on "artgen Studio"
chord(2.02, [C3, E4, G4, B4], 2.2, vel=0.34, bright=0.8)
note(3.0, E5, 1.2, vel=0.2)

# clip: slow arpeggio, chords change every 3.3 s
prog = [[A2, E4, G4, C5], [F2, C4, E4, A4], [C3, E4, G4, B4], [G2, D4, G4, B4]]
step = 3.3 / 4
t0 = 4.0; k = 0
while t0 < TL['clip_end'] - 0.2:
    ch = prog[k % 4]
    note(t0, ch[0], 3.2, vel=0.2, bright=0.7)
    for j, m in enumerate(ch[1:] + [ch[2]]):
        if t0 + j*step < TL['clip_end'] - 0.2:
            note(t0 + j*step, m, 1.2, vel=0.13, bright=0.9)
    t0 += 3.3; k += 1
# a high pentatonic accent on every click, so each choice is heard
acts = json.load(open("actions.json"))
pent = [A5, C6, E5, G5, D5, A5, E5, C6, G5, E5, A5]
clicks = [a for a in acts if a["name"] not in ("title", "scroll", "work-scroll", "end")]
for i, a in enumerate(clicks):
    note(TL['clip_start'] + a["t"] / TL['speed'], pent[i % len(pent)], 0.7, vel=0.09, bright=1.1)

# montage: one note per cut, rising; a low thud on the hole
cuts = TL['montage'][:8]
for i, tc in enumerate(cuts):
    note(tc, [A4, C5, D5, E5, G5, A5, C6, E5][i], 0.6, vel=0.18)
note(TL['montage'][8], A2 - 12, 1.2, vel=0.35, bright=0.4)

# close: resolve, final note on the wordmark
chord(TL['close'] + 0.02, [A2, 57, C4, E4, B4], 3.4, vel=0.34, bright=0.85)
note(TL['close'] + 1.0, E5, 2.0, vel=0.2); note(TL['close'] + 1.2, C5, 1.8, vel=0.15)

y = np.zeros_like(out); a = 0.18
for i in range(1, len(out)): y[i] = y[i-1] + a*(out[i] - y[i-1])
out = 0.75*y + 0.25*out
fade = np.ones(len(out)); fs = int((TOTAL - 1.4)*SR)
fade[fs:int(TOTAL*SR)] = np.linspace(1, 0, int(TOTAL*SR) - fs); fade[int(TOTAL*SR):] = 0
out = (out*fade)[:int(TOTAL*SR)]
out = out / (np.max(np.abs(out)) + 1e-9) * 0.6
os.makedirs("audio/music", exist_ok=True)
with wave.open("audio/music/theme_raw.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "audio/music/theme_raw.wav", "-t", str(TOTAL),
                "-af", f"aecho=0.7:0.35:38|71:0.22|0.14,loudnorm=I=-19:TP=-2:LRA=9,afade=t=out:st={TOTAL-0.2}:d=0.2",
                "-ar", str(SR), "audio/music/theme.wav"], check=True)
os.remove("audio/music/theme_raw.wav")
print("theme.wav", subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "audio/music/theme.wav"], capture_output=True, text=True).stdout.strip())
