# STORYBOARD: Art or BS? game video (X post, 1080x1080, about 29 s, music + SFX, no narration)

Message: "Can you tell real art from AI BS? Play along, then play the real game and climb the ladder."
Arc: hook, play along, demonstration, call to action. Audience: art people on X. It must work muted, so every beat has large text.

Source: `record.mjs` plays one set of the real game page on a local Worker (phone layout, 540 px at 2x density).
All players get the photographs in the same order, so the video uses only the end of the order.
A new player answers sets 1 to 16 through the API off camera. The recording shows set 17 (photographs 161 to 170 of 185).
The three play-along photographs come after set 17 (positions 171, 178 and 182). `build_index.py` stops if one comes earlier.
`config.json` sets the address in the close card and the share text, the recorded set, the answers to miss in each set and the play-along photographs.
`scripts/build_index.py` cuts the recording at its own speeds and writes `timeline.json` and `index.html`.
The times below come from the take of 2026-11-09. They move a little with each take.
Rebuild everything with `bash video/game/build.sh`.

| # | start | end | what | on-screen text | motion | audio |
|---|---|---|---|---|---|---|
| hook | 0.0 | 1.5 | photo 1 full frame | "Real art, or AI BS?", the icon and "Art or BS?" | slow push | low drone, one high note |
| p1 | 1.5 | 4.65 | photo 1 moves into its frame; countdown 3, 2, 1 (1.85-3.35); stamp at 3.35 | "1 of 3", "Real art, or AI BS?", buttons Art / BS; then ART, artist, venue, photo credit | frame settles, bar drains, stamp lands and shakes | three count notes, stamp thud, major chord |
| p2 | 4.65 | 7.6 | photo 2; countdown 4.8-6.3; stamp at 6.3 | "2 of 3", BS, "AI made this room.", "It imitates ..." | same | count, thud, darker chord |
| p3 | 7.6 | 10.55 | photo 3; countdown 7.75-9.25; stamp at 9.25 | "3 of 3", ART and its credit | same | count, thud, major chord |
| ask | 10.55 | 11.65 | white card | "How many did you get?", "Now play the real game." | text rises | open chord |
| clip | 11.65 | 23.6 | the real game, set 17: two answers with their wall labels (1.5x), eight answers fast (8x), the checkpoint with "Set 17", "8/10", rank and share text, tap on Post on X (1.3x) | captions: Tap Art or BS; The wall label tells you the truth; A real room gets its artist and venue.; Ten photographs in each set; Your score and your rank; Then post your score | finger dot and tap rings from the recorder | quiet arpeggio, a tick on every tap |
| post | 23.6 | 26.2 | the text that the page put in its Post on X link, with the preview card of the score | "Post your score", the share text, the card | card rises, squares pop in | pop, two rising notes |
| close | 26.2 | 29.2 | white | icon, "Art or BS?", "Climb the ladder", the address from `config.json` | lines rise | resolve chord, chime |

Play-along photographs (`config.json`): `press-0082` real (Mulyana, Aichi Triennale 2025), `appliance-chorus-v0-6c638bf8` AI (a sound installation after Pilar Albarracín and Nikita Gale), `press-0091` real (Chiara Camoni, Pavilion of Italy, 61st Venice Biennale).
Each can pass for the other kind: two real rooms that look generated, one generated room that looks real.

The third caption depends on the take. If the second photograph of the set is AI, it says "AI copies real works. The label names them." instead.
The local Worker has only the recorded player, so the checkpoint says "#1 of 1 player". The video adds no other names to the ladder.
The order depends on `game/.key`. With a different key, or after new photographs join the game, check the positions in `timeline.json`.
