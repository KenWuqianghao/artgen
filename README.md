# artgen

artgen generates a whole contemporary art biennial: the edition title, the curatorial statement, the artists, their works, the wall labels, the wall texts, the catalogue essays, photographs of the installations and a website for the edition.

It is satire. Every work comes from a pattern that recurs in real biennials of 2022–2026. The research behind it is in [docs/research-notes.md](docs/research-notes.md).

## Quick start

Generate a biennial with placeholder images. This costs nothing:

```bash
python3 -m artgen biennale --seed 5150 --host venice
```

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

## Real images

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

1. **Generate** (`artgen biennale`). Offline and deterministic. The same seed always gives the same edition. The result is `biennales/<seed>-<title>/exhibition.json`.
2. **Render** (`artgen render`). Calls the image model for each work and saves `media/<work>.jpg`.
3. **Build the site** (`artgen site`). Writes a static website to `site/`. It has a home page, a curatorial statement, participants, visitor information, a press page, and one page per work.

Inside the generator:

- **Artists** come from 33 origin pools. Name, birthplace, home cities and the practice they draw on all come from the same pool, so they agree. Each edition includes at least one rediscovered artist who has died and one collective.
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

After you change texts, regenerate an edition with `--overwrite`. Images whose prompts did not change are kept.

## Folders

```
artgen/            the package: gen/ (artists, titles, works, exhibition), write/ (texts), render/, site/
data/              archetypes, lexicon, world, title structures, real-name blocklist
tools/             sources of data/archetypes.json and data/lexicon.json
docs/research/     the research corpus, with source URLs
biennales/         generated editions (exhibition.json and media/; site/ is build output)
video/demo/        the HyperFrames demo video from version 1
```

## Notes

- Every person and institution is fictional, except the theorists that the essays cite. Each work page says that the work does not exist and names the real works its pattern comes from.
- The demo video in `video/demo/` shows version 1 of the generator.
