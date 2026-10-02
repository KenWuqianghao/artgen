"""artgen Studio: curate a biennial in the browser.

The Studio is static. It loads this package and its data into Pyodide (Python compiled to WebAssembly),
so the browser runs the same generator as the command line. Images come from the image library.

  choices()            the lists, toggles and options the Studio shows
  run(opts_json, base) generate an edition and return every page of its website
  build(out)           write the static Studio to a folder
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from . import corpus
from .env import ROOT

FAMILY_LABELS = {
    "textile": "Textiles", "ceramic": "Ceramics", "earth": "Soil and plants", "archive": "Archives", "shrine": "Shrines and altars",
    "figure": "Figures", "sound": "Sound", "found": "Found objects", "painting": "Painting", "video": "Video",
    "performance": "Performance", "light": "Light and neon", "architecture": "Architecture", "scent": "Scent", "digital": "Digital",
}
THEME_LABELS = {"sound": "Listening", "water": "Water and tides", "earth": "Soil and seeds", "carrying": "Carrying",
                "fable": "Fables", "time": "Rest and time", "hospitality": "Hospitality"}
PRESETS = [
    {"id": "all", "label": "Everything", "forms": []},
    {"id": "venice", "label": "Venice 2026", "forms": ["textile", "earth", "figure", "shrine", "sound", "ceramic"]},
    {"id": "documenta", "label": "documenta", "forms": ["archive", "architecture", "found", "textile"]},
    {"id": "whitney", "label": "Whitney", "forms": ["painting", "shrine", "found", "ceramic", "figure"]},
    {"id": "novideo", "label": "No video, please", "forms": [f for f in FAMILY_LABELS if f not in ("video", "digital")]},
]


def _library() -> dict | None:
    path = ROOT / "library" / "index.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def choices() -> str:
    w, lx = corpus.world(), corpus.lexicon()
    lib = _library()
    covered = {e["archetype"] for e in lib["entries"]} if lib else None
    counts: dict[str, int] = {}
    for a in corpus.archetypes():
        if covered is None or a["id"] in covered:
            counts[a["family"]] = counts.get(a["family"], 0) + 1
    return json.dumps({
        "hosts": [{"id": h["id"], "city": h["city"], "country": h["country"],
                   "venues": [v["name"] for v in h["venues"]][:3]} for h in w["hosts"]],
        "themes": [{"id": m["id"], "label": THEME_LABELS.get(m["id"], m["id"]), "titles": m["titles"][:3], "image": m["image"]}
                   for m in lx["metaphors"]],
        "forms": [{"id": f, "label": FAMILY_LABELS[f], "count": counts.get(f, 0)} for f in FAMILY_LABELS if counts.get(f)],
        "presets": PRESETS,
        "identities": [{"name": i["name"], "accent": i["palette"]["accent"], "ground": i["palette"]["ground"],
                        "font": i["display_font"]} for i in w["identities"]],
        "library_size": len(lib["entries"]) if lib else 0,
    })


def run(opts_json: str, base: str) -> str:
    from .gen.exhibition import generate
    from .gen.options import Options
    from .site import STATIC, StudioCtx, render_pages
    o = json.loads(opts_json)
    opts = Options(seed=int(o.get("seed") or 1), works=int(o.get("works") or 16), host=o.get("host") or None,
                   theme=o.get("theme") or None, title=(o.get("title") or "").strip() or None, forms=list(o.get("forms") or []),
                   rediscovered=o.get("rediscovered", "some"), collectives=o.get("collectives", "some"),
                   emerging=o.get("emerging", "some"), jargon=int(o.get("jargon", 2)), identity=o.get("identity") or None)
    ex = generate(opts, library=_library())
    ctx = StudioCtx(base, (STATIC / "site.css").read_text(encoding="utf-8"))
    countries = {a.born_place.rsplit(", ", 1)[-1] for a in ex.artists if a.born_place}
    cmd = ["python3 -m artgen biennale", f"--seed {opts.seed}", f"--works {opts.works}", f"--host {ex.city.lower() if not opts.host else opts.host}"]
    if opts.theme:
        cmd.append(f"--theme {opts.theme}")
    if opts.title:
        cmd.append(f"--title \"{opts.title}\"")
    if opts.forms:
        cmd.append("--forms " + " ".join(opts.forms))
    for k in ("rediscovered", "collectives", "emerging"):
        if getattr(opts, k) != "some":
            cmd.append(f"--{k} {getattr(opts, k)}")
    if opts.jargon != 2:
        cmd.append(f"--jargon {opts.jargon}")
    if opts.identity:
        cmd.append(f"--identity {opts.identity}")
    cmd.append("--library")
    return json.dumps({
        "pages": render_pages(ex, ctx),
        "summary": {
            "edition": ex.edition_name, "title": ex.title, "city": ex.city, "opening": ex.opening, "closing": ex.closing,
            "artists": len(ex.artists), "countries": len(countries), "venues": len(ex.venues),
            "rediscovered": sum(1 for a in ex.artists if a.died_year), "collectives": sum(1 for a in ex.artists if a.collective),
            "identity": ex.identity["name"], "accent": ex.identity["palette"]["accent"], "theme_title": ex.title,
            "director": next(p.name for p in ex.team if "Artistic" in p.role),
        },
        "cli": " ".join(cmd),
        "exhibition": ex.to_dict(),
    }, ensure_ascii=False)


def build(out: Path) -> Path:
    """Copy the Studio page, this package, the data and the image library into one static folder."""
    if out.exists():
        shutil.rmtree(out)
    static = Path(__file__).parent / "studio_static"
    shutil.copytree(static, out)
    # one file holds the package and the data, so the page makes a single request instead of thirty
    bundle: dict[str, str] = {}
    for src in sorted((ROOT / "artgen").rglob("*")):
        if src.is_file() and "__pycache__" not in src.parts and src.suffix in {".py", ".css"} and "studio_static" not in src.parts:
            bundle[str(src.relative_to(ROOT))] = src.read_text(encoding="utf-8")
    for src in sorted((ROOT / "data").glob("*.json")):
        bundle[str(src.relative_to(ROOT))] = src.read_text(encoding="utf-8")
    lib = ROOT / "library"
    if (lib / "index.json").exists():
        bundle["library/index.json"] = (lib / "index.json").read_text(encoding="utf-8")
        shutil.copytree(lib / "media", out / "library" / "media")
    (out / "app.json").write_text(json.dumps(bundle, ensure_ascii=False), encoding="utf-8")
    return out / "index.html"
