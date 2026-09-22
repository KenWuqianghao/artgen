# DESIGN — artgen demo

Brand = the generator's own gallery page (out/index.html) + a terminal. Editorial, museum-label restraint. No accent colour except one gold moment.

## Palette
| role | hex | note |
|---|---|---|
| dark bg | #141414 | terminal + hook + end card |
| dark fg | #ECE8DF | |
| dark muted | #9A948A | ≥ 4.5:1 on #141414 |
| wall (light bg) | #F4F2EE → #E6E2DA | gallery wall gradient, same as placeholder.svg |
| floor | #B8B2A6 → #8F897D | |
| ink | #1A1A1A | |
| light muted | #6F6A61 | 4.9:1 on #F4F2EE |
| gold (once) | #B8963E | end card dot only |

## Type (system fonts — no capture, no live URL)
- Serif: Georgia — titles, quotes, essay text
- Sans: Helvetica Neue / Helvetica — labels, captions, uppercase letter-spaced 0.08em
- Mono: Menlo — terminal

## Components
- Wall label: 340×130 card #FBFAF7, 1px #D6D1C7, artist bold 15px sans, title italic serif 14px, materials 11px sans muted.
- Terminal: #141414, Menlo 30px, prompt "$" muted, output lines fg.

## Do / Don't
- Do hard cuts. Do slow dollies (scale 1.00→1.05). Do let text breathe.
- Don't use whooshes, shaders, gradients other than the wall.
- Don't wink: every on-screen sentence is real generator output, shown deadpan.
