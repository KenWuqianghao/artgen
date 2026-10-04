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

## Folders

```
artgen/            the package: gen/ (artists, titles, works, exhibition), write/ (texts), render/, site/, studio
data/              archetypes, lexicon, world, title structures, real-name blocklist
tools/             sources of data/archetypes.json and data/lexicon.json
library/           pre-rendered images, one per archetype, with what each one shows
docs/research/     the research corpus, with source URLs
biennales/         generated editions (exhibition.json and media/; site/ is build output)
video/demo/        the HyperFrames demo video of the Studio
```

## Notes

- Every person and institution is fictional, except the theorists that the essays cite. Each work page says that the work does not exist and names the real works its pattern comes from.
