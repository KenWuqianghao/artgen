"""Render installation views for every work in an exhibition directory.

Rendering is the only step that costs money, so it is separate from generation and resumable:
a work whose image already matches its prompt is skipped. A changed prompt marks the image stale;
pass force=True to redo it.
"""
from __future__ import annotations

import hashlib
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ..model import Exhibition
from .providers import PROVIDERS, RenderError, default_provider


def _hash(prompt: str, provider: str) -> str:
    return hashlib.sha256(f"{provider}\n{prompt}".encode()).hexdigest()[:16]


def render_exhibition(directory: Path, provider: str | None = None, *, only: list[str] | None = None,
                      force: bool = False, limit: int | None = None, workers: int = 4,
                      log=lambda s: print(s, file=sys.stderr)) -> dict:
    provider = provider or default_provider()
    if provider not in PROVIDERS:
        raise RenderError(f"unknown provider {provider!r}; choose from {', '.join(PROVIDERS)}")
    fn = PROVIDERS[provider]
    ex = Exhibition.load(directory)
    media_dir = directory / "media"
    media_dir.mkdir(exist_ok=True)
    ledger_path = media_dir / "ledger.json"
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}

    # an image belongs to its prompt, not to its slug: reuse any earlier render of an identical prompt
    by_hash = {e["hash"]: e for e in ledger.values() if (media_dir / e["file"]).exists() and e.get("provider") != "dry"}
    reused = []
    for w in ex.works:
        e = by_hash.get(_hash(w.prompt, "openai")) or by_hash.get(_hash(w.prompt, "fal")) or by_hash.get(_hash(w.prompt, "replicate"))
        if e and not force and w.media_kind != "image":
            src = media_dir / e["file"]
            dst = media_dir / f"{w.slug}{src.suffix}"
            if src != dst:
                import shutil
                shutil.copy2(src, dst)
            for old in media_dir.glob(f"{w.slug}.svg"):
                old.unlink()
            w.media, w.media_kind = str(dst.relative_to(directory)), "image"
            ledger[w.slug] = {**e, "file": dst.name}
            reused.append(w.slug)
    if reused:
        ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")
        ex.save(directory)

    todo, skipped, stale = [], [], []
    for w in ex.works:
        if only and w.slug not in only and w.id not in only:
            continue
        h = _hash(w.prompt, provider)
        entry = ledger.get(w.slug)
        has_file = bool(w.media) and (directory / w.media).exists()
        real_already = has_file and w.media_kind == "image"
        if not force and has_file and entry and entry.get("hash") == h:
            skipped.append(w.slug)
            continue
        if not force and real_already and provider == "dry":
            skipped.append(w.slug)          # never replace a paid image with a placeholder
            continue
        if not force and has_file and entry and entry.get("hash") != h and w.media_kind == "image":
            stale.append(w.slug)
            continue
        todo.append(w)
    if limit is not None:
        todo = todo[:limit]

    lock = threading.Lock()
    done, failed = [], []

    def job(w):
        artist = ex.artist(w.artist_id)
        caption = f"{artist.name}, {w.title}, {w.year}"
        path = fn(w.prompt, media_dir / w.slug, caption=caption)
        return w, path

    log(f"render: {len(todo)} to do with {provider}, {len(skipped)} up to date, {len(stale)} stale (use --force)")
    with ThreadPoolExecutor(max_workers=1 if provider == "dry" else workers) as pool:
        futures = {pool.submit(job, w): w for w in todo}
        for fut in as_completed(futures):
            w = futures[fut]
            try:
                w, path = fut.result()
            except Exception as e:  # one failed image must not lose the others
                failed.append((w.slug, str(e)))
                log(f"  failed  {w.slug}: {e}")
                continue
            with lock:
                for old in media_dir.glob(f"{w.slug}.*"):
                    if old == path or old.suffix not in {".svg", ".jpg", ".png"}:
                        continue
                    if old.suffix == ".svg":
                        old.unlink()
                    else:  # never delete a paid image; keep it out of the way
                        (media_dir / "superseded").mkdir(exist_ok=True)
                        old.rename(media_dir / "superseded" / f"{old.stem}-{ledger.get(w.slug, {}).get('hash', 'old')}{old.suffix}")
                w.media = str(path.relative_to(directory))
                w.media_kind = "placeholder" if provider == "dry" else "image"
                ledger[w.slug] = {"hash": _hash(w.prompt, provider), "provider": provider, "file": path.name}
                ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")
                ex.save(directory)
                done.append(w.slug)
                log(f"  done    {w.slug}")
    if reused:
        log(f"render: reused {len(reused)} earlier image(s) with identical prompts")
    return {"done": done, "skipped": skipped + reused, "stale": stale, "failed": failed, "provider": provider}
