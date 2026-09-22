"""Build a single static HTML page that shows every generated work like a catalogue."""
import html
import json
from pathlib import Path


def _md_to_html(md):
    """Very small Markdown subset: paragraphs, *italic*, **bold**, > quote, footnotes, ---."""
    import re
    out = []
    for block in md.split("\n\n"):
        b = block.strip()
        if not b:
            continue
        b = html.escape(b)
        b = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", b)
        b = re.sub(r"\*(.+?)\*", r"<em>\1</em>", b)
        b = re.sub(r"\[\^(\d+)\]:", r"<sup>\1</sup>", b)
        b = re.sub(r"\[\^(\d+)\]", r"<sup>\1</sup>", b)
        if b.startswith("&gt; "):
            out.append(f"<blockquote>{b[5:]}</blockquote>")
        elif b == "---":
            out.append("<hr>")
        else:
            out.append("<p>" + b.replace("\n", "<br>") + "</p>")
    return "\n".join(out)


def build(out_root: Path):
    works = []
    for spec_path in sorted(out_root.glob("*/spec.json")):
        d = spec_path.parent
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        media = None
        for name in ("video.mp4", "image.png", "image.jpg", "placeholder.svg"):
            if (d / name).exists():
                media = f"{d.name}/{name}"
                break
        works.append({
            "spec": spec,
            "media": media,
            "label": (d / "label.md").read_text(encoding="utf-8") if (d / "label.md").exists() else "",
            "statement": (d / "statement.md").read_text(encoding="utf-8") if (d / "statement.md").exists() else "",
            "essay": (d / "essay.md").read_text(encoding="utf-8") if (d / "essay.md").exists() else "",
        })

    cards = []
    for w in works:
        s = w["spec"]
        if w["media"] and w["media"].endswith(".mp4"):
            media_html = f'<video controls muted loop playsinline src="{w["media"]}"></video>'
        elif w["media"]:
            media_html = f'<img src="{w["media"]}" alt="">'
        else:
            media_html = '<div class="nomedia"></div>'
        cards.append(f"""
<article class="work" id="w{len(cards)+1}">
  <figure>{media_html}</figure>
  <div class="label">{_md_to_html(w["label"])}</div>
  <details><summary>Artist statement</summary>{_md_to_html(w["statement"])}</details>
  <details><summary>Curatorial essay</summary><div class="essay">{_md_to_html(w["essay"])}</div></details>
</article>""")

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Foreigners Everywhere, Again</title>
<style>
:root{{--bg:#f6f4ef;--fg:#1a1a1a;--muted:#6f6a61;--rule:#d9d4ca;--card:#fffdf9}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#141414;--fg:#ece8df;--muted:#9a948a;--rule:#2b2b2b;--card:#1c1c1c}}}}
:root[data-theme=dark]{{--bg:#141414;--fg:#ece8df;--muted:#9a948a;--rule:#2b2b2b;--card:#1c1c1c}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 Georgia,"Times New Roman",serif}}
header{{padding:56px 16px 24px;max-width:1080px;margin:0 auto}}
h1{{font-weight:normal;font-size:clamp(28px,5vw,48px);margin:0 0 8px;letter-spacing:-.01em}}
header p{{color:var(--muted);margin:0;font-family:Helvetica,Arial,sans-serif;font-size:13px;letter-spacing:.08em;text-transform:uppercase}}
main{{max-width:1080px;margin:0 auto;padding:0 16px 80px;display:grid;gap:48px}}
.work{{background:var(--card);border:1px solid var(--rule);padding:16px}}
figure{{margin:0 0 16px}}
figure img,figure video{{width:100%;height:auto;display:block;background:#000}}
.nomedia{{aspect-ratio:16/10;background:var(--rule)}}
.label p{{margin:0 0 4px;font-family:Helvetica,Arial,sans-serif;font-size:14px}}
.label p:first-child{{font-size:15px}}
details{{border-top:1px solid var(--rule);margin-top:12px;padding-top:12px}}
summary{{cursor:pointer;font-family:Helvetica,Arial,sans-serif;font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}}
details p{{max-width:66ch}}
blockquote{{margin:16px 0;padding-left:16px;border-left:2px solid var(--rule);color:var(--muted);font-style:italic}}
sup{{font-size:.7em;color:var(--muted)}}
hr{{border:0;border-top:1px solid var(--rule);margin:24px 0}}
@media (min-width:900px){{.work{{display:grid;grid-template-columns:1.2fr 1fr;gap:24px}}.work figure{{grid-row:1/span 3}}}}
</style></head>
<body>
<header>
  <h1>Foreigners Everywhere, Again</h1>
  <p>{len(works)} new commissions · generated {__import__('datetime').date.today().isoformat()} · every word is random</p>
</header>
<main>
{''.join(cards)}
</main>
</body></html>"""
    path = out_root / "index.html"
    path.write_text(page, encoding="utf-8")
    return path
