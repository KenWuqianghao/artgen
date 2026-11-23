"""The AI images of the game "Art or BS?". Each one is the twin of one real photograph in game/real/:
the same kind of room, light, colour and framing, with an artgen work in place of the real one.
So the room and the colours do not tell a player which photograph is real.

  game/ai/manifest.json   entries: id, twin (a game/real id), archetype, variant, look, and prompt after rendering
  game/ai/<id>.jpg        1280 px wide

look holds what a writer saw in the real photograph, never its artwork:
  room    architecture, walls, ceiling, floor, windows, what is visible beyond the room
  light   where the light comes from and its colour
  colour  exposure, contrast, saturation and white balance of the photograph
  camera  position, height, lens, angle, and where the artwork sits in the frame
  people  "none", or who stands where
"""
from __future__ import annotations

import json
import shutil
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import corpus
from .env import ROOT
from .model import Venue
from .prompts import TEXT_FAMILIES_ALLOWED
from .textkit import join_list, sub_rng

DIR = ROOT / "game" / "ai"
MANIFEST = DIR / "manifest.json"
LOOK_FIELDS = ("room", "light", "colour", "camera", "people")


def load() -> list[dict]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if MANIFEST.exists() else []


def _save(entries: list[dict]) -> None:
    MANIFEST.write_text(json.dumps({"entries": entries}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def prompt(entry: dict) -> str:
    from .gen.artist import make_artist
    from .gen.work import make_work
    arch = {a["id"]: a for a in corpus.archetypes()}[entry["archetype"]]
    look = entry["look"]
    rng = sub_rng("twin", entry["id"])
    artist = make_artist(rng, 1, 2027, set(), profile="midcareer")
    venue = Venue(id="twin", name="twin", description=look["room"], floor="", light=look["light"])
    work = make_work(rng, 1, artist, venue, "game", 2027, "Game", arch=arch, pinned={"variant": entry["variant"]})
    people = "No people in the room." if look["people"].strip().lower() == "none" else f"People: {look['people']}"
    text_rule = ("The only legible text is the artwork's own phrase, spelled exactly as given." if arch["id"] in TEXT_FAMILIES_ALLOWED
                 else "No legible text on the artwork; wall labels are small and not readable.")
    return (
        "Installation view photograph from the press kit of a contemporary art biennial or museum exhibition. "
        f"Room: {look['room']} Light: {look['light']} "
        f"The artwork: {work.scene} Materials: {join_list(work.materials)}. "
        f"Framing: {look['camera']} Horizontal 3:2 frame. {people} "
        f"Colour and exposure: {look['colour']} "
        "Style: a real photograph by a professional exhibition photographer, high detail, "
        "the kind of image published on Contemporary Art Daily or a museum press page. Unremarkable and credible. "
        f"Not cinematic: no dramatic spotlight, no lens flare, no haze unless the artwork makes it, no vignette. {text_rule} No watermark."
    )


def check(entries: list[dict], real_ids: set[str]) -> None:
    arch_ids = {a["id"]: len(a["scenes"]) for a in corpus.archetypes()}
    if len({e.get("id") for e in entries}) != len(entries):
        raise SystemExit(f"{MANIFEST.relative_to(ROOT)}: two entries have the same id")
    scenes = Counter((e.get("archetype"), e.get("variant")) for e in entries)
    if repeated := [f"{a} variant {v}" for (a, v), n in scenes.items() if n > 1]:
        # a player who sees an invented work twice in different rooms knows that both are AI
        raise SystemExit(f"{MANIFEST.relative_to(ROOT)}: each scene can have one twin only. Repeated: {', '.join(repeated)}")
    for e in entries:
        where = f"{MANIFEST.relative_to(ROOT)}: entry {e.get('id') or '?'}"
        if e.get("twin") not in real_ids:
            raise SystemExit(f"{where}: twin {e.get('twin')!r} is not in game/real/manifest.json")
        if e.get("archetype") not in arch_ids or not 0 <= e.get("variant", -1) < arch_ids[e["archetype"]]:
            raise SystemExit(f"{where}: no archetype {e.get('archetype')!r} with variant {e.get('variant')!r}")
        look = e.get("look") or {}
        bad = [k for k in LOOK_FIELDS if not isinstance(look.get(k), str) or not look[k].strip()]
        if bad:
            raise SystemExit(f"{where}: look needs {', '.join(bad)}")


def render(provider: str, *, workers: int = 2, only: list[str] | None = None, force: bool = False, log=print) -> list[dict]:
    """Render every entry that has no image yet (or the ones in only, with force). A rerun continues after a failure."""
    from .library import _resize
    from .render.providers import PROVIDERS
    entries = load()
    real = json.loads((ROOT / "game" / "real" / "manifest.json").read_text(encoding="utf-8"))["entries"]
    check(entries, {e["id"] for e in real})
    todo = [e for e in entries if (only is None or e["id"] in only) and (force or not (DIR / f"{e['id']}.jpg").exists())]
    log(f"twins: {len(todo)} of {len(entries)} to render")
    fn, lock, tmp = PROVIDERS[provider], threading.Lock(), DIR / "tmp"
    tmp.mkdir(exist_ok=True)

    def job(e):
        text = prompt(e)
        raw = fn(text, tmp / e["id"], caption=e["archetype"])
        _resize(raw, DIR / f"{e['id']}.jpg")
        raw.unlink(missing_ok=True)
        return text

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(job, e): e for e in todo}
        for fut in as_completed(futures):
            e = futures[fut]
            try:
                text = fut.result()
            except Exception as err:  # keep going; a rerun picks up what failed
                log(f"  failed  {e['id']}: {str(err)[:160]}")
                continue
            with lock:
                e["prompt"] = text
                _save(entries)
                log(f"  done    {e['id']}")
    shutil.rmtree(tmp, ignore_errors=True)
    return entries
