"""Load the JSON corpus in data/. Cached, read-only."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


@lru_cache(maxsize=None)
def load(name: str) -> dict:
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


def world() -> dict:
    return load("world")


def lexicon() -> dict:
    return load("lexicon")


def archetypes() -> list[dict]:
    return load("archetypes")["archetypes"]


def archetype(arch_id: str) -> dict:
    return next(a for a in archetypes() if a["id"] == arch_id)


@lru_cache(maxsize=None)
def real_names() -> frozenset[str]:
    """Names of real artists that appear in the research corpus. Generated names must not collide."""
    path = DATA / "real_names.json"
    if not path.exists():
        return frozenset()
    return frozenset(n.lower() for n in json.loads(path.read_text(encoding="utf-8")))
