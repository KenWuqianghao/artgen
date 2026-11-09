# STORYBOARD: Art or Artifice? game video (X post, 1080x1080, about 28 s, music + SFX, no narration)

Message: "Can you tell a real art installation from an AI one? Play along, then play the real game every day."
Arc: hook, play along, demonstration, call to action. Audience: art people on X. It must work muted, so every beat has large text.

Source: `record.mjs` plays one full round of the real game page on a local Worker (phone layout, 540 px at 2x density).
`config.json` sets the address in the close card and the share text, the three play-along photographs and the answers to miss.
`scripts/build_index.py` cuts the recording at its own speeds and writes `timeline.json` and `index.html`.
The times below come from the take of 2026-11-09 (round 35). They move a little with each take.
Rebuild everything with `bash video/game/build.sh`.

| # | start | end | what | on-screen text | motion | audio |
|---|---|---|---|---|---|---|
| hook | 0.0 | 1.4 | photo 1 full frame | "Is this room real?", "Art or Artifice?" with the icon | slow push | low drone, one high note |
| p1 | 1.4 | 4.55 | photo 1 moves into its frame; countdown 3, 2, 1 (1.75-3.25); stamp at 3.25 | "1 of 3", "Real or AI?", buttons Real / AI; then REAL, artist, venue and year, photo credit | frame settles, bar drains, stamp lands and shakes | three count notes, stamp thud, major chord |
| p2 | 4.55 | 7.5 | photo 2; countdown 4.7-6.2; stamp at 6.2 | "2 of 3", AI, "AI made this room.", "It imitates ..." | same | count, thud, darker chord |
| p3 | 7.5 | 10.45 | photo 3; countdown 7.65-9.15; stamp at 9.15 | "3 of 3", REAL and its credit | same | count, thud, major chord |
| ask | 10.45 | 11.55 | white card | "How many did you get?", "Play ten a day." | text rises | open chord |
| clip | 11.55 | 22.3 | the real game: two answers with their wall labels (1.5x), eight answers fast (7x), result, tap on Post on X (1.3x) | captions: Tap Real or AI; The wall label tells you the truth; AI copies real works. The label names them.; Ten photographs a day; Everyone gets the same ten; Then post your score | finger dot and tap rings from the recorder | quiet arpeggio, a tick on every tap |
| post | 22.3 | 25.0 | the text that the page put in its Post on X link, with the preview card of the score | "Post your score", the share text, the card | card rises, squares pop in | pop, two rising notes |
| close | 25.0 | 28.2 | white | icon, "Art or Artifice?", "A new round every day", the address from `config.json` | lines rise | resolve chord, chime |

Play-along photographs (`config.json`): `press-0020` real (Teresa Solar Abboud, Kunstverein Hannover), `ceremonial-suit-v0-cadac78d` AI, `press-0097` real (Goldin+Senneby, MIT List Visual Arts Center).
Each looks like the other kind: a real room that looks generated, a generated room that looks real.

The second caption depends on the take. If the second photograph of the day is real, it says "A real room gets its artist and venue." instead.
