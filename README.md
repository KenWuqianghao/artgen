# artgen

artgen generates a whole contemporary art biennial: the edition title, the curatorial statement, the artists, their works, the wall labels, the wall texts, the catalogue essays, photographs of the installations and a website for the edition.

It is satire. Every work comes from a pattern that recurs in real biennials of 2022–2026. The research behind it is in [docs/research-notes.md](docs/research-notes.md).

## The Studio: curate your own biennial

The Studio is a web page where you make the choices a curator makes. The edition and its website change as you click.

```bash
python3 -m artgen studio serve
```

Then open http://127.0.0.1:8780.

| Control | What it does |
|---|---|
| Seed and Roll | The seed decides everything you do not choose. Roll picks a new one. |
| Number of works | 6 to 24 works. |
| City | Venice, Lisbon, Kochi, Marseille or Busan, each with its own venues. |
| Curatorial theme | Listening, water, soil, carrying, fables, rest or hospitality. The theme names the edition and its sections. |
| Title | Type your own edition title. The headline changes as you type. |
| Forms of art | Turn 15 forms on or off, or use a preset: Venice 2026, documenta, Whitney, No video, please. |
| Line-up | None, some or many rediscovered artists, collectives and emerging artists. |
| Catalogue theory | Plain, Usual or Unbearable footnotes in the catalogue essays. |
| Visual identity | One of six palettes and display typefaces, or let the seed decide. |
| Surprise me | Random choices for everything. |

The address bar keeps your choices, so **Copy link** shares your exact biennial. The page also shows the command that renders your edition with your own images, and it lets you download its `exhibition.json`.

How it works: the Studio is static. It loads this Python package into the browser with [Pyodide](https://pyodide.org), so the browser runs the same generator as the command line. Images come from the image library below, so no API key and no server code are needed. The page needs an internet connection to load Pyodide and the fonts.

`python3 -m artgen studio build` writes the static Studio to `studio/`. Any static web host can serve that folder.

## Live images in the Studio

The photographs in the Studio are presets from the image library. A visitor can also render a work live. The live image shows the work in the room of the visitor's own edition.

There are two ways to pay for a live image:

- **Free renders.** The hosted Studio gives each visitor 3 free renders per day, on the owner's OpenAI key. A Cloudflare Worker ([worker/src/index.js](worker/src/index.js)) holds the key and counts the renders.
- **The visitor's own key.** The visitor pastes an OpenAI key into the Studio. The browser sends the request directly to OpenAI. The key stays in the tab and never reaches the Worker.

The Worker protects the owner's key in four ways:

- It accepts requests only from the Studio's own address.
- It accepts only artgen installation-view prompts.
- It stops each visitor at `FREE_PER_VISITOR` renders per day, and all visitors together at `FREE_PER_DAY`. Change both in [wrangler.jsonc](wrangler.jsonc).
- It keeps each image. A second request for the same work is free.

Also set a monthly budget in your OpenAI account. That is the last line of defence.

### Run it on your computer

Wrangler reads `OPENAI_API_KEY` from `.env`.

```bash
npm run studio:dev
```

`python3 -m artgen studio serve` still works. It has no Worker, so it offers only presets and the visitor's own key.

### Deploy to Cloudflare

The free plan is enough. Do these steps once:

```bash
npx wrangler login
```

```bash
npx wrangler secret put OPENAI_API_KEY
```

Then deploy. Run the same command after each change:

```bash
npm run studio:deploy
```

## The game: Art or BS?

The game shows one photograph of an installation at a time. You answer **Art** or **BS**. **Art** means that the room is real. **BS** means that AI made the room. Then the page shows the truth and a citation. For a real photograph, the citation gives the artist, the venue and the source. For an AI image, it gives the real works that the image imitates. artgen makes the AI images.

- All players get the same photographs in the same order.
- The answers come in sets of 10. After each set, the page shows your score for the set, your place on the ladder and the **Next set** button. The last set can have fewer than 10 photographs.
- The ladder ranks all players by the number of correct answers. Players with the same number share a place. After the first set, you can put your name on the ladder. The page shows the best 50 names.
- After each set you can share your result. On a phone, **Share** opens the share sheet. **Post on X** opens a new post with the result. **Copy result** copies the result.
- When you have answered all photographs, the page tells you. New photographs come later, and you continue with them.
- Keys: `A` or left arrow for Art, `B` or right arrow for BS, `Enter` or `Space` for the next photograph.

### Play it on your computer

The game needs the Worker, because the Worker keeps the answers. Run:

```bash
npm run studio:dev
```

Open the address that Wrangler prints and add `/game.html`. Under `python3 -m artgen studio serve` the game page says that it has no server.

### Add real photographs

The AI images come from the image library. The real photographs come from `game/real/`. It holds 109 press photographs of real installations. `game/real/sources.tsv` records the image address and the page of each one.

1. Save each photograph as `game/real/<id>.jpg`, 1280 × 853 pixels, the same size as the library images. Use plain sRGB with no colour profile. To convert a photograph with a profile, run `jpgicc -q95 in.jpg out.jpg`.
2. Add one entry for each photograph to `game/real/manifest.json`, as in the example below.
3. Build the Studio again with `python3 -m artgen studio build`, or run one of the `npm run` commands.

```json
{"entries": [
  {"id": "commons-0001", "artist": "Artist name", "title": "Title of the work", "year": "2019",
   "venue": "58th Venice Biennale, Arsenale", "credit": "Photo: Jane Doe, CC BY-SA 4.0",
   "source": "https://commons.wikimedia.org/wiki/File:Example.jpg"}
]}
```

`year` and `credit` can be empty. The other fields are necessary. Use only photographs that you have the right to publish, and give the credit that the licence asks for.

Now the game has 185 photographs: 109 real photographs and 76 library images.

The build encodes every game image again with `ffmpeg` (necessary for the game) and writes it to `studio/game/media/`. The new encoding removes the metadata, so the bytes do not show the kind. A player can still match an AI image to the public library by how it looks. The name is a hash with the secret in `game/.key`, so the name does not show the kind either. The first build makes `game/.key`, and git ignores it. Keep it and use the same file on each computer that deploys: a new key renames every image and resets the crowd statistics. It writes the answers to `worker/src/game_pool.json`. Only the Worker reads that file, and git ignores it.

The order of the photographs is the order of their names. The name is a hash, so the order looks random. A new photograph gets its place in the order, and the other photographs keep their order. A player gets a new photograph next if the player is already past its place. Otherwise the player gets it at its place. When you remove a photograph, the answers to it stay in the scores.

### Game API

All routes answer with JSON. A `POST` must come from the game page itself.

| Route | Body or query | Answer |
|---|---|---|
| `GET /api/game/state` | `?player=<token>` | `{total, answered, correct, rank, players, name, next, set}`. `next` is the address of the next photograph, or `null` after the last one. `set` is `{number, answers}`: the set of the last answer, with one `{guess, image, real, reveal, crowd}` for each answer in it. |
| `POST /api/game/answer` | `{player, index, guess}`, where `index` is the number of answers that the player gave before and `guess` is `"real"` or `"ai"` | `{index, real, reveal, crowd, answered, correct, rank, players, next}`. `409` when `index` is not the number of answers, or when no photograph is left. |
| `POST /api/game/name` | `{player, name}` | `{rank, name}`. Only after the first set. The name has 1 to 20 characters. A second call changes the name of the same row. |
| `GET /api/game/ladder` | `?player=<token>`, which you can omit | `{players, entries}` with the best 50 named players as `{rank, name, correct, answered}`. The row of `player` also has `me: true`. |

`player` is a random token of 16 to 64 characters from `A-Z a-z 0-9 _ -`. The page makes it and keeps it in the browser. `total` is the number of answers plus the number of photographs left. `rank` is 1 plus the number of players with more correct answers, or `null` before the first answer. `players` is the number of players with at least one answer. `crowd` is the percent of players who answered that image correctly, or `null` when fewer than 5 players saw it. A photograph that left the game has `image`, `real` and `reveal` set to `null`. Every route answers `503` when the game has no photographs.

The ladder puts players with the same number of correct answers in this order: fewer answers first, then the earlier last answer. The Worker keeps one Durable Object. It holds each player as `pl:<token>`, the number of players for each number of correct answers as `hist`, and the best 100 named players as `ladder`. Once a day, the Worker deletes the counters of earlier days and the keys of the old daily game (`gp:`, `gl:` and `gs:`).

### Share a result

The share text gives the set number, one square for each answer of the set, the score of the set, your place on the ladder and a link:

```
Art or BS? Set 4
🟩🟥🟩🟩🟥🟩🟩🟩🟥🟩 8/10
#12 on the ladder
https://<host>/s/8
```

The link gives the score out of 10. For a short last set, the page rounds the score to a score out of 10: 4 of 5 gives `/s/8`.

`GET /s/<score>` makes the link preview. The Worker answers with a short page for crawlers. Its preview tags show the card of that score, `/share/<score>.jpg`. The page then sends people to `/game`. When the score is not a whole number from 0 to 10, the Worker redirects to `/game`. The game page `/game` shows `/share/card.jpg`. The Worker makes the preview addresses on `/game` absolute for the host, so the cards also work on a custom domain.

The cards are 1200 × 630 JPEGs in `artgen/studio_static/share/`. To make them again, run:

```bash
npm ci
node tools/share_cards.mjs
```

The same script makes the icon of the game and the Studio: `icon.svg`, `apple-touch-icon.png` (180 × 180) and `icon-512.png` in `artgen/studio_static/`.

The script needs Chrome or Chromium. It looks on the `PATH` and in the Playwright and Puppeteer caches. To use a different browser, set `CHROME` to its path. The cards use only images from the image library. They never use the real photographs in `game/real/`, because those belong to their artists.

## Quick start on the command line

Generate a biennial with placeholder images. This costs nothing:

```bash
python3 -m artgen biennale --seed 5150 --host venice
```

Use the images from the library instead of placeholders:

```bash
python3 -m artgen biennale --seed 5150 --host venice --library
```

The same choices as in the Studio are available as flags: `--theme`, `--title`, `--forms`, `--rediscovered`, `--collectives`, `--emerging`, `--jargon`, `--identity` and `--works`. Run `python3 -m artgen biennale --help` for the values.

Open the website it prints, or serve it:

```bash
python3 -m artgen serve biennales/5150-neighbours-everywhere
```

Print one work with its label and wall text:

```bash
python3 -m artgen work --seed 3
```

List the 76 work archetypes and the real works each one generalises:

```bash
python3 -m artgen archetypes
```

## The image library

`library/` holds one installation view for each of the 76 work archetypes. Each image is pinned to what it shows: the scene variant, the materials and the visible details. When an edition uses the library, every work keeps those fixed and is placed in a venue whose room looks like the room in the photograph. Text a photograph cannot show, such as the artist, the place, the facts and the quotes, still changes. That is how the Studio gets real-looking images with zero rendering.

To add images for new archetypes, or to collect the images of editions you rendered:

```bash
python3 -m artgen library build --provider openai
```

Images that already exist are reused. The 76 current images cost about $4–6 by public price lists.

## Your own images

Put an API key in `.env` (see `.env.example`). Then render the installation views of an existing biennial:

```bash
python3 -m artgen render biennales/5150-neighbours-everywhere --provider openai
```

- The default model is `gpt-image-2.5-flare` at medium quality, 1536 × 1024. Change it with `ARTGEN_OPENAI_MODEL`, `ARTGEN_OPENAI_QUALITY` and `ARTGEN_OPENAI_SIZE`.
- One edition of 18 works took about three minutes. By public price lists it costs roughly $1–2 at medium quality; check your own billing.
- Rendering is resumable. A work that already has an image for the same prompt is skipped. A paid image is never deleted; a replaced one moves to `media/superseded/`.
- If the API rate-limits you, the renderer waits and retries. Use `--workers 1` on a low-tier account.
- `fal` and `replicate` providers are also available. They are not tested.

## How it works

The pipeline has three separate steps, so you only pay for images once:

1. **Generate** (`artgen biennale`). Offline and deterministic. The same seed and choices always give the same edition. The result is `biennales/<seed>-<title>/exhibition.json`.
2. **Render** (`artgen render`), or use the library. Saves `media/<work>.jpg`.
3. **Build the site** (`artgen site`). Writes a static website to `site/`. It has a home page, a curatorial statement, participants, visitor information, a press page, and one page per work.

Inside the generator:

- **Artists** come from 33 origin pools. Name, birthplace, home cities and the practice they draw on all come from the same pool, so they agree.
- **Works** come from archetypes in `data/archetypes.json`. An archetype owns its scene, compatible materials, medium line, facts, process notes, artist quotes, closing sentence and camera framing. That is why the label, the wall text and the photograph describe the same object.
- **Texts** follow the structures found in the research. Wall texts are plain and specific. Catalogue essays are dense with theory, as they are in real catalogues.
- **Each edition gets its own visual identity**: one of six palettes and display typefaces, like real biennials.

## Edit the corpus

| What | Where | Then run |
|---|---|---|
| Work archetypes | `tools/build_archetypes.py` | `python3 tools/build_archetypes.py` |
| Sentence patterns, edition metaphors | `tools/build_lexicon.py` | `python3 tools/build_lexicon.py` |
| Artwork title structures | `data/lexicon_titles.json` | nothing |
| Names, cities, venues, identities | `data/world.json` | nothing |

After you change texts, regenerate an edition with `--overwrite`. Images whose prompts did not change are kept. Rebuild the Studio afterwards.

## Demo video

`video/demo/renders/artgen-studio-demo.mp4` is a 39-second demo for social media. It is a real recording of the Studio, with captions, zooms, a montage from the library and composed music.

To rebuild it, serve the Studio and run the build script:

```bash
python3 -m artgen studio serve
```

```bash
bash video/demo/build.sh
```

The script records the Studio with a scripted browser, then builds the composition, the music and the sound effects from the recorded action times, checks it and renders it. It needs Node.js, ffmpeg and the packages in `package.json` (`npm install`).

## Game video

`video/game/renders/art-or-bs.mp4` is a 29-second square video of the game for X. It works with the sound off. It starts with three photographs to guess, then shows a recording of one set on the real game page, the checkpoint after the set, the share text and the address.

To rebuild it, run the build script:

```bash
bash video/game/build.sh
```

The script builds the Studio and starts a local Worker with an empty game state. A new player answers the sets before the recorded set through the API. Then a scripted browser plays the recorded set, and the script stops the Worker. Then it cuts the recording, builds the composition, the music and the sound effects, checks the composition and renders it. It needs Node.js, ffmpeg, the packages in `package.json` (`npm ci`), `game/.key` and Chrome. To use a different Chrome, set `CHROME` to its path. On a computer with little free memory, set `WORKERS=1`.

`video/game/config.json` holds the address in the video, the recorded set, the answers that the recording gets wrong in each set and the three photographs to guess. To show a different address, change `url` and run the build script again. The browser sends that address to the local Worker, so the recorded page and its share text show it too.

All players get the photographs in the same order, so the video must not show the answers of the first sets. The video records set 17 (photographs 161 to 170 of 185). The three photographs to guess come after set 17 in the order. The build stops if a photograph to guess comes earlier. The order depends on `game/.key`, so use the key of the live game. If the game gets new photographs, check the positions in `video/game/timeline.json`.

## Folders

```
artgen/            the package: gen/ (artists, titles, works, exhibition), write/ (texts), render/, site/, studio
data/              archetypes, lexicon, world, title structures, real-name blocklist
tools/             sources of data/archetypes.json and data/lexicon.json, and the share cards of the game
library/           pre-rendered images, one per archetype, with what each one shows
game/real/         real photographs for the game Art or BS?, with their citations
worker/            the Cloudflare Worker: live renders and the game
docs/research/     the research corpus, with source URLs
biennales/         generated editions (exhibition.json and media/; site/ is build output)
video/demo/        the HyperFrames demo video of the Studio
video/game/        the HyperFrames video of the game Art or BS?
```

## Notes

- Every person and institution is fictional, except the theorists that the essays cite. Each work page says that the work does not exist and names the real works its pattern comes from.
