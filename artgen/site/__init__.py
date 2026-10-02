"""Build a static microsite for one exhibition directory: <dir>/site/."""
from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

from ..model import Artist, Exhibition, Work

STATIC = Path(__file__).parent / "static"
E = html.escape


class Ctx:
    """How pages refer to each other, to images and to the stylesheet.
    The static build uses relative files; the Studio preview uses in-page links and inline CSS."""
    studio = False

    def up(self, depth: int) -> str:
        return "../" * depth

    def page(self, name: str, depth: int) -> str:
        return f"{self.up(depth)}{name}.html"

    def work(self, w: Work, depth: int) -> str:
        return f"{self.up(depth)}works/{w.slug}.html"

    def media(self, w: Work, depth: int) -> str:
        return f"{self.up(depth)}media/{Path(w.media).name}" if w.media else ""

    def css(self, depth: int) -> str:
        return f'<link rel="stylesheet" href="{self.up(depth)}site.css">'


STUDIO_JS = """<script>
document.addEventListener("click", function (e) {
  var a = e.target.closest("a[href^='#']");
  if (!a) return;
  e.preventDefault();
  parent.postMessage({artgenNav: a.getAttribute("href").slice(1)}, "*");
});
</script>"""


class StudioCtx(Ctx):
    studio = True

    def __init__(self, base: str, css_text: str):
        self.base, self.css_text = base.rstrip("/") + "/", css_text

    def page(self, name: str, depth: int) -> str:
        return f"#page/{name}"

    def work(self, w: Work, depth: int) -> str:
        return f"#work/{w.slug}"

    def media(self, w: Work, depth: int) -> str:
        return self.base + w.media if w.media else ""

    def css(self, depth: int) -> str:
        # the preview regenerates on every keystroke: no entrance animation
        return f"<style>{self.css_text}\n.hero h1 {{ animation: none !important; }}</style>"


# ------------------------------------------------------------------ text to html

def _inline(text: str) -> str:
    t = E(text)
    t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
    t = re.sub(r"\[\^(\d+)\]", r'<sup id="r\1"><a href="#n\1">\1</a></sup>', t)
    return t


def paragraphs(blocks: list[str]) -> str:
    out = []
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        if b.startswith("> "):
            out.append(f"<blockquote>{_inline(b[2:])}</blockquote>")
        else:
            out.append(f"<p>{_inline(b)}</p>")
    return "\n".join(out)


def essay_html(essay: str) -> tuple[str, str]:
    body, _, notes = essay.partition("\n---\n")
    body_html = paragraphs(body.split("\n\n"))
    items = []
    for line in notes.strip().splitlines():
        m = re.match(r"\[\^(\d+)\]:\s*(.*)", line.strip())
        if m:
            items.append(f'<li id="n{m.group(1)}">{_inline(m.group(2))} <a href="#r{m.group(1)}" aria-label="Back to text">↩</a></li>')
    notes_html = f'<div class="notes"><ol>{"".join(items)}</ol></div>' if items else ""
    return body_html, notes_html


# ------------------------------------------------------------------ page shell

NAV = [("index.html", "Exhibition"), ("statement.html", "Statement"), ("participants.html", "Participants"),
       ("visit.html", "Visit"), ("press.html", "Press")]


def head(ex: Exhibition, title: str, depth: int, ctx: Ctx) -> str:
    idn = ex.identity
    fonts = idn.get("google_fonts", "")
    font_link = (f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                 f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">') if fonts else ""
    pal = idn.get("palette", {})
    tokens = ";".join(f"--{k}:{v}" for k, v in pal.items())
    disp = idn.get("display_font")
    extra = []
    if disp:
        extra.append(f'--display:"{disp}", var(--ui)')
    if idn.get("display_weight"):
        extra.append(f"--display-weight:{idn['display_weight']}")
    if idn.get("display_tracking"):
        extra.append(f"--display-tracking:{idn['display_tracking']}")
    style = ";".join([tokens] + extra)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(ex.edition_name)}: {E(ex.title)}. {E(ex.city)}, {E(ex.opening)} to {E(ex.closing)}.">
{font_link}
{ctx.css(depth)}
<style>:root{{{style}}}</style>
</head><body>"""


def bar(ex: Exhibition, depth: int, current: str, ctx: Ctx) -> str:
    links = "".join(
        f'<a href="{ctx.page(href.removesuffix(".html"), depth)}"{" aria-current=\"page\"" if href == current else ""}>{label}</a>' for href, label in NAV)
    return f"""<header class="bar"><div class="wrap">
<a class="edition" href="{ctx.page("index", depth)}">{E(ex.edition_name)}</a>
<nav aria-label="Main">{links}</nav></div></header><main>"""


def foot(ex: Exhibition, ctx: Ctx) -> str:
    director = next((p for p in ex.team if "Artistic" in p.role), ex.team[0])
    return f"""</main><footer><div class="wrap">
<div><p>{E(ex.edition_name)}</p><p><em>{E(ex.title)}</em></p><p>{E(ex.city)}, {E(ex.opening)} – {E(ex.closing)}</p></div>
<div><p>Organised by {E(ex.institution)}</p><p>{E(director.role)}: {E(director.name)}</p></div>
<div><p>{len(ex.artists)} participants</p><p>{len(ex.works)} works</p><p>{len(ex.venues)} venues</p></div>
<p class="fine">{"Curated by you in artgen Studio. " if ctx.studio else ""}This biennial does not exist. Every artist, work, text and photograph on this site was generated at random by artgen (seed {ex.seed}). Any resemblance to a real exhibition is the point.</p>
</div></footer>{STUDIO_JS if ctx.studio else ""}</body></html>"""


# ------------------------------------------------------------------ fragments

def img(w: Work, depth: int, alt: str, ctx: Ctx, eager: bool = False) -> str:
    src = ctx.media(w, depth)
    if not src:
        return '<div style="aspect-ratio:3/2;background:var(--rule)"></div>'
    loading = "" if eager else ' loading="lazy"'
    return f'<img src="{E(src)}" alt="{E(alt)}" width="1536" height="1024"{loading}>'


def alt_text(w: Work, a: Artist) -> str:
    return f"Installation view of {a.name}, {w.title}, {w.year}: {w.scene}"


def photo_caption(ex: Exhibition, w: Work, a: Artist) -> str:
    v = ex.venue(w.venue_id)
    return (f"{E(a.name)}, <em>{E(w.title)}</em>, {w.year}. Installation view, {E(ex.edition_name)}, "
            f"{E(v.name)}. {E(w.courtesy)}. Photo: {E(w.photo_credit)}")


def tile(ex: Exhibition, w: Work, span: int, depth: int, ctx: Ctx) -> str:
    a = ex.artist(w.artist_id)
    return f"""<a class="tile" style="--span:{span}" href="{ctx.work(w, depth)}">
{img(w, depth, alt_text(w, a), ctx)}
<div class="cap"><div class="who">{E(a.name)}</div><div class="what"><em>{E(w.title)}</em>, {w.year}</div><div class="medium">{E(w.medium)}</div></div></a>"""


SPANS = [[7, 5], [5, 7], [4, 4, 4], [6, 6], [8, 4], [4, 8]]


def grid(ex: Exhibition, works: list[Work], depth: int, ctx: Ctx, offset: int = 0) -> str:
    out, i, row = [], 0, offset
    while i < len(works):
        pattern = SPANS[row % len(SPANS)]
        chunk = works[i:i + len(pattern)]
        if len(chunk) < len(pattern):
            pattern = [12 // len(chunk)] * len(chunk)
        out += [tile(ex, w, s, depth, ctx) for w, s in zip(chunk, pattern)]
        i += len(chunk)
        row += 1
    return f'<div class="grid">{"".join(out)}</div>'


def label_card(ex: Exhibition, w: Work, a: Artist) -> str:
    lines = [f'<p class="artist">{E(a.name)}</p>', f'<p class="life">{E(a.life_line)}</p>',
             f'<p><span class="title">{E(w.title)}</span>, {w.year}</p>', f'<p class="medium">{E(w.medium)}</p>']
    if w.dimensions:
        lines.append(f'<p class="dims">{E(w.dimensions)}</p>')
    lines.append(f'<p class="small">{E(w.courtesy)}. {E(w.support)}</p>')
    return f'<aside class="label" aria-label="Wall label">{"".join(lines)}</aside>'


def join_basis(w: Work) -> str:
    basis = w.extra.get("basis", [])
    if len(basis) <= 1:
        return "".join(basis)
    return "; ".join(basis[:-1]) + "; and " + basis[-1]


# ------------------------------------------------------------------ pages

def title_size(ex: Exhibition) -> str:
    """Large, but never so large that the longest word has to break: em width per letter differs by typeface."""
    longest = max((len(w) for w in ex.title.split()), default=8)
    per_letter = ex.identity.get("display_width", 0.62)
    fit = 88 / max(1.0, longest * per_letter)          # vw that lets the longest word fit the column
    return f"clamp(34px, min(12.5vw, {fit:.2f}vw), 232px)"


def page_home(ex: Exhibition, ctx: Ctx) -> str:
    first_tile = ex.works_in(ex.sections[0].id)[0] if ex.sections and ex.works_in(ex.sections[0].id) else None
    candidates = [w for w in ex.works if w.media_kind == "image" and w is not first_tile]
    preferred = [w for w in candidates if w.family in ("textile", "figure", "earth", "found", "architecture")]
    lead = (preferred or candidates or ex.works)[0]
    la = ex.artist(lead.artist_id)
    director = next((p for p in ex.team if "Artistic" in p.role), ex.team[0])
    venues = ", ".join(v.name for v in ex.venues[:3]) + (" and other venues" if len(ex.venues) > 3 else "")
    sections = []
    for i, s in enumerate(ex.sections):
        works = ex.works_in(s.id)
        if not works:
            continue
        sections.append(f"""<section class="block" id="{s.id}"><div class="wrap">
<div class="section-head"><h2>{E(s.title)}</h2><p>{_inline(s.text)}</p></div>
{grid(ex, works, 0, ctx, offset=i)}</div></section>""")
    names = '<span class="sep"> / </span>'.join(
        f'<a href="{ctx.work(_first_work(ex, a), 0)}">{E(a.name)}</a>' for a in sorted(ex.artists, key=lambda a: a.sort_name))
    return head(ex, f"{ex.title}: {ex.edition_name}", 0, ctx) + bar(ex, 0, "index.html", ctx) + f"""
<section class="hero"><div class="wrap">
<h1 style="font-size:{title_size(ex)}">{E(ex.title)}</h1>
<div class="facts">
<p><span class="k">{E(ex.edition_name)}</span><br>{E(ex.city)}, {E(ex.opening)} – {E(ex.closing)}</p>
<p><span class="k">{E(director.role)}</span><br>{E(director.name)}</p>
<p><span class="k">Venues</span><br>{E(venues)}</p>
</div></div></section>
<section class="lead-image"><div class="wrap"><figure>
<a href="{ctx.work(lead, 0)}">{img(lead, 0, alt_text(lead, la), ctx, eager=True)}</a>
<figcaption>{photo_caption(ex, lead, la)}</figcaption></figure></div></section>
<section class="block"><div class="wrap prose">{paragraphs(ex.statement[:2])}
<p><a class="more" href="{ctx.page("statement", 0)}">Read the full curatorial statement</a></p></div></section>
{"".join(sections)}
<section class="block"><div class="wrap"><h2>Participants</h2><p class="names">{names}</p></div></section>
""" + foot(ex, ctx)


def _first_work(ex: Exhibition, a: Artist) -> Work:
    return next(w for w in ex.works if w.artist_id == a.id)


def page_statement(ex: Exhibition, ctx: Ctx) -> str:
    team = "".join(f"<p><strong>{E(p.name)}</strong>, {E(p.role)}<br><span class='byline'>{E(p.bio)}</span></p>" for p in ex.team)
    return head(ex, f"Curatorial statement: {ex.edition_name}", 0, ctx) + bar(ex, 0, "statement.html", ctx) + f"""
<section class="block"><div class="wrap"><h2>{E(ex.title)}</h2>
<div class="prose">{paragraphs(ex.statement)}</div></div></section>
<section class="block"><div class="wrap"><h2>Curatorial team</h2><div class="cols">{team}</div></div></section>
""" + foot(ex, ctx)


def page_participants(ex: Exhibition, ctx: Ctx) -> str:
    items = []
    for a in sorted(ex.artists, key=lambda a: a.sort_name):
        ws = [w for w in ex.works if w.artist_id == a.id]
        links = ", ".join(f'<a href="{ctx.work(w, 0)}"><em>{E(w.title)}</em></a>' for w in ws)
        items.append(f'<li id="{a.id}"><div class="n">{E(a.name)}</div><div class="l">{E(a.life_line)}</div><div>{links}</div></li>')
    return head(ex, f"Participants: {ex.edition_name}", 0, ctx) + bar(ex, 0, "participants.html", ctx) + f"""
<section class="block"><div class="wrap"><h2>Participants</h2><ul class="roster">{"".join(items)}</ul></div></section>
""" + foot(ex, ctx)


def page_visit(ex: Exhibition, ctx: Ctx) -> str:
    venues = "".join(f"<div><h3>{E(v.name)}</h3><p>{E(v.description)}</p></div>" for v in ex.venues)
    return head(ex, f"Visit: {ex.edition_name}", 0, ctx) + bar(ex, 0, "visit.html", ctx) + f"""
<section class="block"><div class="wrap"><h2>Visit</h2><div class="prose">{paragraphs(ex.visitor_info)}</div></div></section>
<section class="block"><div class="wrap"><h2>Venues</h2><div class="cols">{venues}</div></div></section>
""" + foot(ex, ctx)


def page_press(ex: Exhibition, ctx: Ctx) -> str:
    credits = "".join(f"<li>{photo_caption(ex, w, ex.artist(w.artist_id))}</li>" for w in ex.works if w.media)
    return head(ex, f"Press: {ex.edition_name}", 0, ctx) + bar(ex, 0, "press.html", ctx) + f"""
<section class="block"><div class="wrap"><h2>Press release</h2><div class="prose">{paragraphs(ex.press_release)}</div></div></section>
<section class="block"><div class="wrap"><h2>Image captions</h2><ol class="notes">{credits}</ol></div></section>
""" + foot(ex, ctx)


def page_work(ex: Exhibition, i: int, ctx: Ctx) -> str:
    w = ex.works[i]
    a = ex.artist(w.artist_id)
    prev_w = ex.works[i - 1] if i > 0 else None
    next_w = ex.works[i + 1] if i + 1 < len(ex.works) else None
    body, notes = essay_html(w.essay)
    pager = ['<nav class="pager" aria-label="More works">']
    pager.append(f'<a href="{ctx.work(prev_w, 1)}"><span class="dir">Previous</span>{E(ex.artist(prev_w.artist_id).name)}</a>' if prev_w else "<span></span>")
    pager.append(f'<a href="{ctx.work(next_w, 1)}" style="text-align:right"><span class="dir">Next</span>{E(ex.artist(next_w.artist_id).name)}</a>' if next_w else "<span></span>")
    pager.append("</nav>")
    section = ex.section(w.section_id)
    return head(ex, f"{a.name}, {w.title}: {ex.edition_name}", 1, ctx) + bar(ex, 1, "", ctx) + f"""
<article class="wrap">
<figure class="work-image" style="margin:24px 0 0">{img(w, 1, alt_text(w, a), ctx, eager=True)}
<figcaption>{photo_caption(ex, w, a)}</figcaption></figure>
<div class="work-body">
{label_card(ex, w, a)}
<div>
<section class="walltext prose"><h2>About the work</h2>{paragraphs(w.wall_text.split(chr(10) * 2))}</section>
<section class="bio prose"><h2>About the artist</h2>{paragraphs([a.bio])}</section>
<section class="essay prose"><h2>From the catalogue</h2><p class="byline">{E(w.essay_author)}</p>{body}{notes}</section>
<p class="byline" style="margin-top:32px">Shown in <a href="{ctx.page("index", 1)}">{E(section.title)}</a>, {E(ex.venue(w.venue_id).name)}.</p>
<p class="pattern">This work does not exist. It was generated from a pattern that recurs in recent biennials, for example in {E(join_basis(w))}.</p>
</div></div>
{"".join(pager)}
</article>
""" + foot(ex, ctx)


# ------------------------------------------------------------------ build

def render_pages(ex: Exhibition, ctx: Ctx) -> dict[str, str]:
    pages = {"page/index": page_home(ex, ctx), "page/statement": page_statement(ex, ctx),
             "page/participants": page_participants(ex, ctx), "page/visit": page_visit(ex, ctx), "page/press": page_press(ex, ctx)}
    for i, w in enumerate(ex.works):
        pages[f"work/{w.slug}"] = page_work(ex, i, ctx)
    return pages


def build(directory: Path) -> Path:
    ex = Exhibition.load(directory)
    ctx = Ctx()
    site = directory / "site"
    if site.exists():
        shutil.rmtree(site)
    (site / "works").mkdir(parents=True)
    (site / "media").mkdir()
    shutil.copy(STATIC / "site.css", site / "site.css")
    for w in ex.works:
        src = directory / w.media if w.media else None
        if src and not src.exists() and w.media.startswith("library/"):
            from ..env import ROOT
            src = ROOT / w.media
        if src and src.exists():
            shutil.copy(src, site / "media" / Path(w.media).name)
    for key, content in render_pages(ex, ctx).items():
        kind, name = key.split("/", 1)
        target = site / (f"{name}.html" if kind == "page" else f"works/{name}.html")
        target.write_text(content, encoding="utf-8")
    return site / "index.html"
