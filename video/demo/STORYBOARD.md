# STORYBOARD: artgen Studio demo (X post, 1920x1080, about 39 s, music + SFX, no narration)

Message: "You can curate your own contemporary art biennial, and it looks exactly like the real ones."
Arc: Demonstration. Audience: art-world people on X. Must read muted, so every step has a caption.

Source: `record.mjs` drives the real Studio (seeded Math.random, 1280x720 at 1.5x density).
`actions.json` gives the time of each action; video time = 4.0 + t / 1.2 (clip sped up 1.2x).
`scripts/build_index.py` turns actions.json into index.html and timeline.json, so the exact times below shift with each take.
Rebuild everything with `bash video/demo/build.sh` while the Studio is served.

| # | start | end | what | motion | audio |
|---|---|---|---|---|---|
| b1 | 0.0 | 2.0 | dark. "Every biennale looks the same." | words stagger in, slow push | low drone, hard stop |
| b2 | 2.0 | 4.0 | dark. "So we built one you can curate." then "artgen Studio" | lines rise | held chord, high note at 3.0 |
| clip | 4.0 | 30.5 | the real Studio: roll seed, city, theme, forms, line-up, theory, identity, typed title, a work page, Surprise me | zoom 1.15x on the title while it is typed; zoom 1.25x on the work page (23.7-26.6) | soft arpeggio; tick on every click; typing clicks 17.0-18.7 |
| montage | 30.5 | 35.0 | 9 library photos, 0.45 s cuts; last (a hole in the floor) holds 0.9 s | slow push per photo | note per cut; low thud on the hole |
| close | 35.0 | 38.6 | dark. "artgen Studio", "Curate a biennial that does not exist.", "Every artist, work, text and photograph is generated." | lines rise, fade out | resolve, final note at 36.0 |

Captions (bottom right, over the preview): Roll a seed; Choose a city; Choose a curatorial theme; Decide which art is allowed;
Add rediscovered artists; Set the catalogue theory to Unbearable; Pick a visual identity; Name your biennial;
Every work has an installation view; and a wall label, a wall text and a footnoted essay; Or let it surprise you.
