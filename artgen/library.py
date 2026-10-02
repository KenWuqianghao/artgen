"""The image library: one pre-rendered installation view per archetype (or more), each pinned to the
scene variant, materials and visual details it shows. With a library, editions need no rendering at all,
which is what lets the Studio run in a browser.

  library/index.json        entries: archetype, variant, core, accent, visual, room, prompt, file
  library/media/<id>.jpg    1280 px wide
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import corpus
from .env import ROOT
from .model import Exhibition, Venue
from .textkit import sub_rng

LIB = ROOT / "library"


def load_library(path: Path = LIB) -> dict:
    index = path / "index.json"
    if not index.exists():
        sys.exit("artgen: no image library yet. Run 'python3 -m artgen library build --provider openai'.")
    return json.loads(index.read_text(encoding="utf-8"))


def _save(index: dict, path: Path = LIB) -> None:
    (path / "index.json").write_text(json.dumps(index, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def _resize(src: Path, dst: Path, width: int = 1280) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if shutil.which("sips"):
        subprocess.run(["sips", "-Z", str(width), "-s", "formatOptions", "82", str(src), "--out", str(dst)],
                       check=True, capture_output=True)
    elif shutil.which("ffmpeg"):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", f"scale={width}:-2", "-q:v", "4", str(dst)], check=True)
    else:
        shutil.copy2(src, dst)


def _entry_id(arch: str, variant: int, prompt: str) -> str:
    return f"{arch}-v{variant}-{hashlib.sha256(prompt.encode()).hexdigest()[:8]}"


def collect_from_biennales(index: dict, root: Path = ROOT / "biennales") -> int:
    """Add every rendered work of every generated edition to the library (free: the images exist already)."""
    have = {e["id"] for e in index["entries"]}
    added = 0
    for ex_json in sorted(root.glob("*/exhibition.json")):
        ex = Exhibition.load(ex_json.parent)
        for w in ex.works:
            if w.media_kind != "image" or "visual" not in w.extra:
                continue
            eid = _entry_id(w.archetype, w.extra["variant"], w.prompt)
            if eid in have:
                continue
            dst = LIB / "media" / f"{eid}.jpg"
            _resize(ex_json.parent / w.media, dst)
            index["entries"].append({"id": eid, "archetype": w.archetype, "variant": w.extra["variant"],
                                     "core": w.extra["core"], "accent": w.extra["accent"], "visual": w.extra["visual"],
                                     "room": ex.venue(w.venue_id).room, "prompt": w.prompt, "file": f"library/media/{eid}.jpg",
                                     "source": ex.slug})
            have.add(eid)
            added += 1
    return added


def plan_missing(index: dict) -> list[dict]:
    """One new pinned work for every archetype that has no image yet, in a Venice room that suits it."""
    from .gen.artist import make_artist
    from .gen.work import make_work
    from .prompts import image_prompt
    covered = {e["archetype"] for e in index["entries"]}
    venice = next(h for h in corpus.world()["hosts"] if h["id"] == "venice")
    plans = []
    for arch in corpus.archetypes():
        if arch["id"] in covered:
            continue
        rng = sub_rng("library", arch["id"])
        artist = make_artist(rng, 1, 2027, set(), profile="rediscovered" if arch.get("historical") and rng.random() < 0.2 else "midcareer")
        fitting = [Venue(**v) for v in venice["venues"] if arch["family"] in v["families"]] or [Venue(**venice["venues"][0])]
        venue = fitting[rng.randrange(len(fitting))]
        variant = rng.randrange(len(arch["scenes"]))
        work = make_work(rng, 1, artist, venue, "library", 2027, "Library", arch=arch, pinned={"variant": variant})
        prompt = image_prompt(rng, work, venue)
        eid = _entry_id(arch["id"], variant, prompt)
        plans.append({"id": eid, "archetype": arch["id"], "variant": variant, "core": work.extra["core"],
                      "accent": work.extra["accent"], "visual": work.extra["visual"], "room": venue.room,
                      "prompt": prompt, "file": f"library/media/{eid}.jpg", "source": "library"})
    return plans


def build(provider: str, *, workers: int = 2, limit: int | None = None, dry_run: bool = False, log=print) -> dict:
    from .render.providers import PROVIDERS
    LIB.mkdir(exist_ok=True)
    (LIB / "media").mkdir(exist_ok=True)
    index = json.loads((LIB / "index.json").read_text()) if (LIB / "index.json").exists() else {"entries": []}
    added = collect_from_biennales(index)
    _save(index)
    log(f"library: {added} image(s) collected from generated editions, {len(index['entries'])} in total")
    plans = plan_missing(index)
    if limit is not None:
        plans = plans[:limit]
    log(f"library: {len(plans)} archetype(s) still need an image")
    if dry_run or not plans:
        return index
    fn = PROVIDERS[provider]
    lock = threading.Lock()
    tmp = LIB / "tmp"
    tmp.mkdir(exist_ok=True)

    def job(plan):
        raw = fn(plan["prompt"], tmp / plan["id"], caption=plan["archetype"])
        _resize(raw, LIB / plan["file"].removeprefix("library/"))
        raw.unlink(missing_ok=True)
        return plan

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(job, p): p for p in plans}
        for fut in as_completed(futures):
            p = futures[fut]
            try:
                fut.result()
            except Exception as e:  # keep going; a rerun picks up what failed
                log(f"  failed  {p['archetype']}: {str(e)[:160]}")
                continue
            with lock:
                index["entries"].append(p)
                _save(index)
                log(f"  done    {p['archetype']}")
    shutil.rmtree(tmp, ignore_errors=True)
    return index
