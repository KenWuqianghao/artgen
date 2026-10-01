# Research notes

artgen generates fictional biennial works. To make them realistic, we studied real works and real texts from major exhibitions of 2022–2026. This file summarises what we found and how the generator uses it.

## The corpus

The raw research is in [docs/research](research/). Every record has a source URL. Descriptions are paraphrased. Quotations are short.

| File | Scope | Records |
|---|---|---|
| `venice2026.json` | Venice 2026, "In Minor Keys": main exhibition, national pavilions | 48 works |
| `us_uk_venice2024.json` | Venice 2024, Whitney 2024 and 2026, Barbican "Unravel", Tate Turbine Hall, Carnegie 2022 | 45 works |
| `global_south.json` | Sharjah 16, São Paulo 2025, Dak'Art 2024, Kochi-Muziris 2025–26, Diriyah 2024 and 2026, documenta fifteen, Bangkok 2024 | 53 works |
| `europe_asia.json` | Berlin 13, Gwangju 2024 and 2026, Istanbul 2025, Lyon 2024, Manifesta 15, Liverpool 2025, Taipei and Shanghai 2025, Art Basel Unlimited | 54 works |
| `part_labels.json` | Wall label formats (Whitney, Tate, MoMA, Venice, Gwangju, Berlin, documenta, Sharjah) | 30 labels, 26 rules |
| `part_walltexts.json` | Sentence structure of wall texts (Tate, Whitney, AIC, Hammer, ICA Boston) | 14 texts, 15 rules |
| `part_bios_press.json` | Artist bios and e-flux press language | 53 bio patterns, 81 phrases |
| `part_photo.json` | Installation photography and caption formats | 22 traits, 73 captions |

In total: 200 works from 29 exhibitions.

## What the works have in common

1. **Material over image.** Textiles are the largest group (27 of 200), then earth, soil and plants (21). Video is small (7).
2. **Hand-made at large scale.** Hundreds of vessels, thousands of tiles, kilometres of rope. A number in the wall text proves the labour.
3. **Materials that change.** Flowers rot, resin melts, mud tiles crumble, salt dissolves, seeds sprout.
4. **Senses other than sight.** Scent, sound through the floor, rooms you enter with a torch.
5. **Shrines and altars.** Candles, photographs, objects of friends who died.
6. **Archives and schools.** Reading rooms, seed libraries, kitchens, rooms "for rest".
7. **Rediscovered artists.** Each edition shows artists who died without recognition, often next to new commissions.
8. **Hybrid figures.** Bronze beings that are part human, part animal, part tree, placed as "sentinels".

## What the texts have in common

- **Wall texts are plain.** They do not use theory words. The order is: what the work is, a sourced fact with a number and a place, the artist's own words, a process detail, a theme sentence with "explores" or "draws on", and a closing sentence that turns a physical fact into a meaning.
- **Catalogue essays carry the theory.** Glissant, Sharpe, Haraway, Tsing and others appear here, with page numbers.
- **Edition titles** are short verb phrases ("to carry"), fables ("The Three-Legged Cat"), poem lines ("You must change your life") or metaphors ("In Minor Keys", "Bedrock").
- **Curatorial statements** follow a fixed order: announcement, origin of the title, the concept, a "time of crisis" paragraph, the method (motifs instead of sections), the host city, a modest claim about what art can do, an invitation.
- **Labels** in Venice 2026 read "Born 1983, Manila, Philippines. Lives in London, UK". Deceased artists read "D. 2017". Collectives read "Founded 2008, Dakar, Senegal".

## What critics say

Critics repeat the same complaints across editions: the hang is overstuffed, the themes are broad enough to fit anything, the wall text does the work that the object cannot do, and the same artists appear at every biennial. Dean Kissick summarised it as "progressive in content, conservative in form" (Harper's, December 2024).

## Photographs

Real installation views are horizontal, evenly lit and mostly empty of people. Rooms show their floors, walls and a view into the next room. Retouchers remove exit signs and cables. Image models do the opposite by default: a single spotlight, silhouettes, haze. The prompts in `artgen/prompts.py` ask for the real conventions.

## How the generator uses this

- `tools/build_archetypes.py` turns recurring patterns into 76 work archetypes. Each archetype lists the real works it generalises in `basis`. The website shows this list on every work page.
- `tools/build_lexicon.py` holds the sentence patterns for wall texts, essays, bios, statements and press releases.
- `data/world.json` holds names, cities, venues and identities. All people and institutions in it are fictional, except the cited theorists.
- `data/real_names.json` lists the real artists in the corpus. Generated names that match one of them are rejected.

## Limits

- Frieze, Artsy, Artnet and Ocula often blocked automated reading, so these sources are under-used.
- Most `photo_notes` fields are empty because written sources rarely describe the photographs.
- The corpus reflects large international exhibitions. It does not describe commercial galleries or local art scenes.
