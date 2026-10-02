"""artgen command line.

  artgen biennale [--seed N] [--works N] [--host venice] [--render openai] [--out biennales]
  artgen render DIR [--provider openai] [--only SLUG ...] [--force] [--limit N]
  artgen site DIR
  artgen serve DIR [--port 8000]
  artgen work [--seed N] [--archetype ID] [--family F]
  artgen archetypes
"""
from __future__ import annotations

import argparse
import http.server
import functools
import random
import sys
from pathlib import Path

from . import corpus
from .env import ROOT, load_dotenv


class _Server(http.server.ThreadingHTTPServer):
    request_queue_size = 128     # browsers open many connections at once; the default of 5 resets some


def _dir(path: str) -> Path:
    d = Path(path)
    if not (d / "exhibition.json").exists():
        sys.exit(f"artgen: {d} has no exhibition.json. Run 'artgen biennale' first.")
    return d


def _keep_media_that_still_fits(out: Path, ex) -> None:
    """On --overwrite: reattach images whose work slug and prompt are unchanged; drop placeholders for vanished works."""
    import json
    media = out / "media"
    if not media.exists():
        return
    ledger_path = media / "ledger.json"
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
    from .render import _hash
    slugs = {w.slug: w for w in ex.works}
    for f in media.iterdir():
        if f.suffix == ".svg" and f.stem not in slugs:
            f.unlink()
    for slug, entry in list(ledger.items()):
        w = slugs.get(slug)
        f = media / entry["file"]
        if w and f.exists() and entry.get("hash") == _hash(w.prompt, entry["provider"]):
            w.media, w.media_kind = f"media/{f.name}", ("placeholder" if entry["provider"] == "dry" else "image")
        elif not w and entry.get("provider") == "dry":
            ledger.pop(slug)          # paid entries stay: render reuses them by prompt hash
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")


def _copy_library_media(out: Path, ex) -> None:
    """Make a library-backed edition self-contained: its images live in its own media/ like rendered ones."""
    import json
    import shutil
    from .render import _hash
    media = out / "media"
    media.mkdir(parents=True, exist_ok=True)
    ledger_path = media / "ledger.json"
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
    for w in ex.works:
        if w.media and w.media.startswith("library/"):
            dst = media / f"{w.slug}.jpg"
            shutil.copy2(ROOT / w.media, dst)
            for old in media.glob(f"{w.slug}.svg"):
                old.unlink()
            w.media, w.media_kind = f"media/{dst.name}", "image"
            ledger[w.slug] = {"hash": _hash(w.prompt, "openai"), "provider": "openai", "file": dst.name, "from": "library"}
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")


def cmd_biennale(args):
    from .gen.exhibition import generate
    from .gen.options import Options
    from .render import render_exhibition
    from .site import build
    seed = args.seed if args.seed is not None else random.randint(1, 99999)
    opts = Options(seed=seed, works=args.works, host=args.host, theme=args.theme, title=args.title,
                   forms=args.forms or [], rediscovered=args.rediscovered, collectives=args.collectives,
                   emerging=args.emerging, jargon=args.jargon, identity=args.identity)
    library = None
    if args.library:
        from .library import load_library
        library = load_library()
    ex = generate(opts, library=library)
    out = Path(args.out) / ex.slug
    if out.exists() and (out / "exhibition.json").exists() and not args.overwrite:
        sys.exit(f"artgen: {out} exists. Use --overwrite to replace its texts (images are kept).")
    _keep_media_that_still_fits(out, ex)
    if library:
        _copy_library_media(out, ex)
    ex.save(out)
    print(f"{ex.edition_name}: {ex.title}")
    print(f"  {ex.city}, {ex.opening} – {ex.closing}; {len(ex.artists)} artists, {len(ex.works)} works, {len(ex.venues)} venues")
    print(f"  saved {out / 'exhibition.json'}")
    render_exhibition(out, args.render or "dry", workers=args.workers)
    page = build(out)
    print(f"  site  {page}")


def cmd_render(args):
    from .render import render_exhibition
    from .site import build
    d = _dir(args.dir)
    res = render_exhibition(d, args.provider, only=args.only, force=args.force, limit=args.limit, workers=args.workers)
    print(f"done {len(res['done'])}, up to date {len(res['skipped'])}, stale {len(res['stale'])}, failed {len(res['failed'])} ({res['provider']})")
    for slug, err in res["failed"]:
        print(f"  failed {slug}: {err}")
    print(f"site {build(d)}")


def cmd_site(args):
    from .site import build
    print(build(_dir(args.dir)))


def cmd_serve(args):
    site = _dir(args.dir) / "site"
    if not site.exists():
        from .site import build
        build(Path(args.dir))
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(site))
    with _Server(("127.0.0.1", args.port), handler) as httpd:
        print(f"serving {site} at http://127.0.0.1:{args.port}/  (Ctrl+C to stop)")
        httpd.serve_forever()


def cmd_work(args):
    from .gen.artist import make_artist
    from .gen.work import make_work, pick_archetype
    from .model import Venue
    from .prompts import image_prompt
    from .textkit import sub_rng
    from .write.walltext import wall_text
    seed = args.seed if args.seed is not None else random.randint(1, 99999)
    rng = sub_rng(seed, "single")
    artist = make_artist(rng, 1, 2027, set())
    arch = corpus.archetype(args.archetype) if args.archetype else pick_archetype(rng, artist, [args.family] if args.family else None)
    host = corpus.world()["hosts"][0]
    venue = Venue(**next((v for v in host["venues"] if arch["family"] in v["families"]), host["venues"][0]))
    w = make_work(rng, 1, artist, venue, "main", 2027, "1st Lagoon Biennial", arch=arch)
    print(f"{artist.name}\n{artist.life_line}\n\n{w.title}, {w.year}\n{w.medium}\n{w.dimensions}\n{w.courtesy}\n")
    print(wall_text(rng, artist, w, "1st Lagoon Biennial"))
    print(f"\n[archetype {arch['id']}; based on: {'; '.join(arch['basis'])}]")
    if args.prompt:
        print("\n" + image_prompt(rng, w, venue))


def cmd_library(args):
    from .library import build
    if args.action == "build":
        idx = build(args.provider, workers=args.workers, limit=args.limit, dry_run=args.dry_run)
        print(f"library: {len(idx['entries'])} images covering {len({e['archetype'] for e in idx['entries']})} of {len(corpus.archetypes())} archetypes")


def cmd_studio(args):
    from .studio import build
    out = Path(args.out)
    page = build(out)
    print(f"studio {page}")
    if args.action == "serve":
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(out))
        with _Server(("127.0.0.1", args.port), handler) as httpd:
            print(f"serving the Studio at http://127.0.0.1:{args.port}/  (Ctrl+C to stop)")
            httpd.serve_forever()


def cmd_archetypes(args):
    rows = sorted(corpus.archetypes(), key=lambda a: (a["family"], a["id"]))
    for a in rows:
        print(f"{a['family']:<13} {a['id']:<24} w{a['weight']}  {a['basis'][0]}")
    print(f"\n{len(rows)} archetypes")


def main(argv=None):
    load_dotenv()
    p = argparse.ArgumentParser(prog="artgen", description="Generate a contemporary art biennial: works, texts, installation views and a website.")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("biennale", help="generate a whole biennial into a folder and build its website")
    b.add_argument("--seed", type=int)
    b.add_argument("--works", type=int, default=16)
    b.add_argument("--host", choices=[h["id"] for h in corpus.world()["hosts"]])
    b.add_argument("--theme", choices=[m["id"] for m in corpus.lexicon()["metaphors"]], help="curatorial metaphor")
    b.add_argument("--title", help="your own edition title")
    b.add_argument("--forms", nargs="*", choices=sorted({a["family"] for a in corpus.archetypes()}), help="allowed forms of art")
    b.add_argument("--rediscovered", choices=["none", "some", "many"], default="some")
    b.add_argument("--collectives", choices=["none", "some", "many"], default="some")
    b.add_argument("--emerging", choices=["none", "some", "many"], default="some")
    b.add_argument("--jargon", type=int, choices=[1, 2, 3], default=2, help="density of theory in catalogue essays")
    b.add_argument("--identity", choices=[i["name"] for i in corpus.world()["identities"]])
    b.add_argument("--library", action="store_true", help="use pre-rendered images from library/ instead of rendering")
    b.add_argument("--render", choices=["dry", "openai", "fal", "replicate"], help="image provider; default dry (no cost)")
    b.add_argument("--workers", type=int, default=2)
    b.add_argument("--out", default=str(ROOT / "biennales"))
    b.add_argument("--overwrite", action="store_true")
    b.set_defaults(func=cmd_biennale)

    r = sub.add_parser("render", help="render installation views for an existing biennial (resumable)")
    r.add_argument("dir")
    r.add_argument("--provider", choices=["dry", "openai", "fal", "replicate"])
    r.add_argument("--only", nargs="*")
    r.add_argument("--force", action="store_true")
    r.add_argument("--limit", type=int)
    r.add_argument("--workers", type=int, default=2, help="parallel requests; image APIs rate-limit hard")
    r.set_defaults(func=cmd_render)

    s = sub.add_parser("site", help="rebuild the website of a biennial")
    s.add_argument("dir")
    s.set_defaults(func=cmd_site)

    v = sub.add_parser("serve", help="serve a biennial's website on localhost")
    v.add_argument("dir")
    v.add_argument("--port", type=int, default=8000)
    v.set_defaults(func=cmd_serve)

    w = sub.add_parser("work", help="print one work with its label and wall text")
    w.add_argument("--seed", type=int)
    w.add_argument("--archetype")
    w.add_argument("--family")
    w.add_argument("--prompt", action="store_true", help="also print the image prompt")
    w.set_defaults(func=cmd_work)

    lb = sub.add_parser("library", help="build the image library that lets editions (and the Studio) skip rendering")
    lb.add_argument("action", choices=["build"])
    lb.add_argument("--provider", default="openai", choices=["dry", "openai", "fal", "replicate"])
    lb.add_argument("--workers", type=int, default=2)
    lb.add_argument("--limit", type=int)
    lb.add_argument("--dry-run", action="store_true", help="only report what would be rendered")
    lb.set_defaults(func=cmd_library)

    st = sub.add_parser("studio", help="build or serve the Studio: curate a biennial in the browser")
    st.add_argument("action", choices=["build", "serve"])
    st.add_argument("--out", default=str(ROOT / "studio"))
    st.add_argument("--port", type=int, default=8780)
    st.set_defaults(func=cmd_studio)

    a = sub.add_parser("archetypes", help="list work archetypes and the real works they generalise")
    a.set_defaults(func=cmd_archetypes)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
