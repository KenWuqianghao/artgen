# STORYBOARD — artgen demo (X post, 1920×1080, 20.7 s, fast pacing, music + SFX, no narration)

Message: "Contemporary art and its catalogue essay can be generated at random, and you cannot tell."
Arc: Reveal. Audience: art-world friends on X. Must read muted.

All copy below is verbatim output of `python3 -m artgen generate -n 6 --seed 100`.

| # | start | end | what | camera / motion | audio |
|---|---|---|---|---|---|
| b1 | 0.0 | 1.6 | dark. serif: "Every biennale looks the same." | words stagger in, scale 1→1.04 | drone |
| b2 | 1.6 | 3.4 | dark. "So we automated it." then terminal prompt types `artgen generate -n 6 --seed 100` | type-on 2.2→3.2 | typing clicks |
| b3 | 3.4 | 6.2 | terminal prints 6 real result lines, one per 0.4 s | y drift −20px | tick per line |
| b4 | 6.2 | 8.6 | gallery wall, real wall label card (Mireille Kowalczyk, *The Weight of Lead*, 2025 …) | card rises, dolly 1→1.06 | Cmaj7 chord |
| b5 | 8.6 | 11.4 | light. big serif quote from the real artist statement | SplitText word stagger, x parallax | arpeggio |
| b6 | 11.4 | 13.6 | light. 4 real footnotes stack | each line fades up | suspension |
| b6b | 13.6 | 15.7 | three real gpt-image-1 renders of installation works (seed 300), hard cuts every 0.7 s, caption with artist and title | push 1→1.04 each | tick per cut, soft note |
| b7 | 15.7 | 17.5 | placeholder.svg full frame: "THE WORK IS NOT HERE. THIS IS THE POINT." | dolly 1.02→1.08 | chime + resolve |
| b8 | 17.5 | 19.1 | dark. counters: 6 works · 6 essays · 24 footnotes · 0.4 s | numbers count up | ticks |
| b9 | 19.1 | 20.7 | dark. wordmark "artgen" + line "random contemporary art, with the paper." + gold dot | scale 0.96→1, dot pops | final note + pop, fade |

Asset audit: no live URL captured. Signature visual = the generator's own placeholder.svg and its real text output. Fonts = system (Georgia, Helvetica, Menlo).
