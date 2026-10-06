"""artgen Studio: curate a biennial in the browser.

The Studio is static. It loads this package and its data into Pyodide (Python compiled to WebAssembly),
so the browser runs the same generator as the command line. Images come from the image library.

  choices()            the lists, toggles and options the Studio shows
  run(opts_json, base) generate an edition and return every page of its website
  build(out)           write the static Studio to a folder, and the image pool of the game "Real or artgen?"
"""
from __future__ import annotations

import hashlib
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


def run(opts_json: str, base: str, live_json: str = "{}") -> str:
    """live_json maps an image prompt to the address of an image rendered live for it."""
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
    data = ex.to_dict()                       # the download keeps library images, never a browser-only address
    live = json.loads(live_json or "{}")
    works = []
    for w in ex.works:
        prompt = w.extra.get("live_prompt") or w.prompt
        if prompt in live:
            w.media, w.media_kind, w.extra["live"] = live[prompt], "image", True
        works.append({"slug": w.slug, "prompt": prompt, "live": prompt in live,
                      "label": f"{ex.artist(w.artist_id).name}, {w.title}"})
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
        "works": works,
        "exhibition": data,
    }, ensure_ascii=False)


REAL_FIELDS = ("artist", "title", "year", "venue", "credit", "source")
REAL_MIN = 6


def _game_pool(out: Path) -> dict:
    """Copy the images of the game to out/game/media and return the key that says which ones are real.

    A public file name is a hash, so the name does not show the kind. The key goes to the Worker, never to the browser."""
    pool: dict[str, list] = {"real": [], "ai": []}
    manifest, lib = ROOT / "game" / "real" / "manifest.json", _library()
    real = json.loads(manifest.read_text(encoding="utf-8"))["entries"] if manifest.exists() else []
    if len(real) < REAL_MIN or not lib:
        return pool
    media = out / "game" / "media"
    media.mkdir(parents=True)

    def publish(kind: str, ident: str, src: Path) -> str:
        img = hashlib.sha256(f"artgen-game:{kind}:{ident}".encode()).hexdigest()[:16]
        shutil.copyfile(src, media / f"{img}.jpg")
        return img

    if len({e.get("id") for e in real}) != len(real):
        raise SystemExit("game/real/manifest.json: two entries have the same id")
    for e in real:
        bad = [k for k in ("id", *REAL_FIELDS) if not isinstance(e.get(k), str) or (k not in ("year", "credit") and not e[k].strip())]
        if bad:
            raise SystemExit(f"game/real/manifest.json: entry {e.get('id') or '?'} needs {', '.join(bad)}")
        src = manifest.parent / f"{e['id']}.jpg"
        if not src.exists():
            raise SystemExit(f"game/real/manifest.json: no image {src.relative_to(ROOT)}")
        pool["real"].append({"img": publish("real", e["id"], src), "reveal": {k: e[k] for k in REAL_FIELDS}})
    forms = {a["id"]: a for a in corpus.archetypes()}
    for e in lib["entries"]:
        a = forms[e["archetype"]]
        pool["ai"].append({"img": publish("ai", e["id"], ROOT / e["file"]), "reveal": {"form": a["form"], "basis": a["basis"]}})
    return pool


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
    (ROOT / "worker" / "src" / "game_pool.json").write_text(json.dumps(_game_pool(out), ensure_ascii=False), encoding="utf-8")
    return out / "index.html"
