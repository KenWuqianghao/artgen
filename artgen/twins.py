from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
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
TMP = DIR / "tmp"
LOOK_FIELDS = ("room", "light", "colour", "camera", "people")


def load() -> list[dict]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if MANIFEST.exists() else []


def _save(entries: list[dict]) -> None:
    TMP.mkdir(exist_ok=True)
    tmp = TMP / MANIFEST.name
    tmp.write_text(json.dumps({"entries": entries}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, MANIFEST)


def prompt(entry: dict) -> str:
    from .gen.artist import make_artist
    from .gen.work import make_work
    arch = {a["id"]: a for a in corpus.archetypes()}[entry["archetype"]]
    look = entry["look"]
    rng = sub_rng("twin", entry["id"])
    artist = make_artist(rng, 1, 2027, set(), profile="midcareer")
    venue = Venue(id="twin", name="twin", description="", floor="", light="")
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
    if unknown := sorted({str(e.get("twin")) for e in entries} - real_ids):
        raise SystemExit(f"{MANIFEST.relative_to(ROOT)}: twin {', '.join(unknown)} is not in game/real/manifest.json")
    copies = Counter(e.get("twin") for e in entries)
    if bad := sorted(r for r in real_ids if copies[r] != 1):
        raise SystemExit(f"{MANIFEST.relative_to(ROOT)}: each real photograph needs exactly one twin. Not so for: {', '.join(bad)}")
    scenes = Counter((e.get("archetype"), e.get("variant")) for e in entries)
    if repeated := [f"{a} variant {v}" for (a, v), n in scenes.items() if n > 1]:
        raise SystemExit(f"{MANIFEST.relative_to(ROOT)}: each scene can have one twin only. Repeated: {', '.join(repeated)}")
    for e in entries:
        where = f"{MANIFEST.relative_to(ROOT)}: entry {e.get('id') or '?'}"
        variant = e.get("variant")
        if e.get("archetype") not in arch_ids or type(variant) is not int or not 0 <= variant < arch_ids[e["archetype"]]:
            raise SystemExit(f"{where}: no archetype {e.get('archetype')!r} with variant {e.get('variant')!r}")
        look = e.get("look") or {}
        bad = [k for k in LOOK_FIELDS if not isinstance(look.get(k), str) or not look[k].strip()]
        if bad:
            raise SystemExit(f"{where}: look needs {', '.join(bad)}")


def fields_hash(entry: dict) -> str:
    fields = {k: entry.get(k) for k in ("twin", "archetype", "variant", "look")}
    return hashlib.sha256(json.dumps(fields, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def stale(entry: dict) -> bool:
    return entry.get("inputs") != fields_hash(entry)


def _fit(src: Path, dst: Path) -> None:
    tmp = TMP / f"{dst.stem}.fit.jpg"
    # crop in RGB: on 4:2:0 input, crop rounds the odd height 853 down to 852
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", str(src), "-vf",
                    "scale=1280:853:force_original_aspect_ratio=increase,format=rgb24,crop=1280:853,sidedata=mode=delete:type=ICC_PROFILE",
                    "-map_metadata", "-1", "-q:v", "2", str(tmp)], check=True)
    os.replace(tmp, dst)


def render(provider: str, *, workers: int = 2, only: list[str] | None = None, force: bool = False, log=print) -> list[str]:
    from .render.providers import PROVIDERS
    if not shutil.which("ffmpeg"):
        raise SystemExit("Rendering twins needs ffmpeg. Install ffmpeg first.")
    entries = load()
    real = json.loads((ROOT / "game" / "real" / "manifest.json").read_text(encoding="utf-8"))["entries"]
    check(entries, {e["id"] for e in real})
    if unknown := sorted(set(only or []) - {e["id"] for e in entries}):
        raise SystemExit(f"{MANIFEST.relative_to(ROOT)}: no entry {', '.join(unknown)}")
    todo = [e for e in entries if (only is None or e["id"] in only)
            and (force or not (DIR / f"{e['id']}.jpg").exists() or stale(e))]
    log(f"twins: {len(todo)} of {len(entries)} to render")
    fn, failed = PROVIDERS[provider], []
    TMP.mkdir(exist_ok=True)

    def job(e):
        text = prompt(e)
        raw = fn(text, TMP / e["id"], caption=e["archetype"])
        _fit(raw, DIR / f"{e['id']}.jpg")
        raw.unlink(missing_ok=True)
        return text

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(job, e): e for e in todo}
        for fut in as_completed(futures):
            e = futures[fut]
            try:
                e["prompt"], e["inputs"] = fut.result(), fields_hash(e)
            except Exception as err:
                failed.append(e["id"])
                log(f"  failed  {e['id']}: {str(err)[:160]}")
                continue
            _save(entries)
            log(f"  done    {e['id']}")
    shutil.rmtree(TMP, ignore_errors=True)
    return failed
