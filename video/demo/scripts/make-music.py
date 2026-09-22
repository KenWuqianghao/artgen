#!/usr/bin/env python3
"""Music bed for the artgen demo, composed to the beat map. Deterministic, no samples.
A minor, 72 BPM, felt-piano-ish additive tone. Run from video/demo: python3 scripts/make-music.py
  0.0–1.6   hook        low drone A2 with a rubbed B2, hard stop
  1.6–3.4   automate    Am(add9) held, one high note as the command finishes (3.2)
  3.4–6.2   terminal    slow arpeggio Am7 → Fmaj7, one note per 0.4 s line
  6.2–8.6   label       Cmaj7 held, sparse
  8.6–11.4  quote       arpeggio Fmaj7 → Dm7
  11.4–13.6 footnotes   E7sus suspension (lift)
  13.6–15.4 the work    resolve Am(add9) + high E, decays
  15.4–17.0 stats       sparse ticks C5 E5 G5 A5 on counters
  17.0–18.6 wordmark    final Am chord, note on the dot (17.55), fade to end
"""
import math, os, subprocess, wave
import numpy as np

SR = 48000; TOTAL = 18.6
out = np.zeros(int(TOTAL * SR) + SR)
def midi(n): return 440.0 * 2 ** ((n - 69) / 12)
def note(t0, m, dur, vel=0.5, bright=1.0):
    n = int(dur * SR)
    if n <= 0: return
    t = np.arange(n) / SR; f = midi(m)
    env = np.exp(-t / (dur * 0.35)) * (1 - np.exp(-t / 0.006))
    sig = (np.sin(2*math.pi*f*t) + 0.35*bright*np.sin(2*math.pi*2*f*t + 0.3)
           + 0.12*bright*np.sin(2*math.pi*3*f*t + 0.7) + 0.05*np.sin(2*math.pi*4*f*t))
    sig += 0.25*np.sin(2*math.pi*f*1.003*t)
    s = int(t0 * SR); end = min(len(out), s + n)
    out[s:end] += (sig * env * vel)[:end - s]
def chord(t0, notes, dur, vel=0.4, spread=0.012, bright=1.0):
    for i, m in enumerate(notes): note(t0 + i*spread, m, dur, vel, bright)

A2, B2, E2, F2, C3, D3, E3, F3, A3 = 45, 47, 40, 41, 48, 50, 52, 53, 57
C4, D4, E4, F4, G4, A4, B4, C5, D5, E5, G5, A5 = 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 79, 81

# hook drone
n = int(1.6 * SR); t = np.arange(n) / SR
drone = 0.22*np.sin(2*math.pi*midi(A2)*t) + 0.12*np.sin(2*math.pi*midi(B2)*t) + 0.08*np.sin(2*math.pi*midi(A2-12)*t)
drone *= np.minimum(1, t / 0.15) * (0.6 + 0.4 * t / 1.6)
out[:n] += drone
# automate
chord(1.65, [A2, E4, A4, B4], 2.0, vel=0.34, spread=0.02, bright=0.8)
note(3.2, E5, 1.0, vel=0.22)
# terminal arpeggio, one note per line (3.6, 4.0, ... 5.6)
arp = [A2, E4, G4, C5, F3, E4, A4]
for i, m in enumerate(arp):
    note(3.6 + i*0.4, m, 1.4, vel=0.30 if m < 60 else 0.24, bright=0.9)
# label
chord(6.25, [C3, E4, G4, B4], 2.4, vel=0.34, spread=0.02, bright=0.8)
note(7.4, G5, 1.2, vel=0.18)
# quote arpeggio Fmaj7 -> Dm7 (one note per word-ish, 0.35 s)
arp2 = [F2, A4, C5, E5, D3, F4, A4, C5]
for i, m in enumerate(arp2):
    note(8.7 + i*0.35, m, 1.3, vel=0.26 if m < 60 else 0.2, bright=1.0)
# footnotes suspension E7sus, one soft note per footnote
chord(11.45, [E2, B4, D5, A4], 2.2, vel=0.32, spread=0.02)
for i in range(4): note(11.55 + i*0.38, [E4, G4, A4, B4][i], 1.0, vel=0.14)
# the work: resolve
chord(13.6, [A2, A3, C4, E4, B4], 1.9, vel=0.4, spread=0.025, bright=0.9)
note(13.65, E5, 1.8, vel=0.2)
# stats ticks
for i, m in enumerate([C5, E5, G5, A5]):
    note(15.5 + i*0.3, m, 0.9, vel=0.18)
# wordmark
chord(17.05, [A2, A3, E4, A4, C5], 1.6, vel=0.38, spread=0.025, bright=0.85)
note(17.55, E5, 1.05, vel=0.22)

y = np.zeros_like(out); a = 0.18
for i in range(1, len(out)): y[i] = y[i-1] + a * (out[i] - y[i-1])
out = 0.75 * y + 0.25 * out
fade = np.ones(len(out)); fs = int((TOTAL - 1.2) * SR)
fade[fs:int(TOTAL*SR)] = np.linspace(1, 0, int(TOTAL*SR) - fs); fade[int(TOTAL*SR):] = 0
out = (out * fade)[:int(TOTAL * SR)]
out = out / (np.max(np.abs(out)) + 1e-9) * 0.6
os.makedirs("audio/music", exist_ok=True)
with wave.open("audio/music/theme_raw.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "audio/music/theme_raw.wav", "-t", str(TOTAL),
                "-af", "aecho=0.7:0.35:38|71:0.22|0.14,loudnorm=I=-19:TP=-2:LRA=9,afade=t=out:st=%s:d=0.2" % (TOTAL - 0.2),
                "-ar", str(SR), "audio/music/theme.wav"], check=True)
os.remove("audio/music/theme_raw.wav")
print("theme.wav", subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","audio/music/theme.wav"],capture_output=True,text=True).stdout.strip(), "s")
