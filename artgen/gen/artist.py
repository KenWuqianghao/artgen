"""Generate artists. Profiles follow the career shapes that dominate recent biennial line-ups."""
from __future__ import annotations

import random

from .. import corpus
from ..model import Artist
from ..textkit import fill, pick, slugify, weighted

# share of each profile in a typical line-up
PROFILES = [
    {"id": "midcareer", "weight": 46},     # b. 1975-1990, lives between two cities
    {"id": "emerging", "weight": 14},      # b. 1990-1997
    {"id": "elder", "weight": 10},         # b. 1938-1955, self-taught or long overlooked, still working
    {"id": "rediscovered", "weight": 16},  # deceased, shown in a historical section
    {"id": "collective", "weight": 14},
]


def _name(rng: random.Random, region: dict, taken: set[str], reserve: bool = True) -> tuple[str, str]:
    """A name from one origin pool. Reserved names also claim their surname, so one edition
    does not show two unrelated artists called Painemal. Falls back to any unused full name."""
    blocked = corpus.real_names()
    for strict in (True, False):
        for _ in range(60):
            first, last = pick(rng, region["first"]), pick(rng, region["last"])
            name = f"{first} {last}"
            if name.lower() in blocked or name in taken or first == last:
                continue
            if strict and reserve and f"last:{last}" in taken:
                continue
            if reserve:
                taken.add(f"last:{last}")
            return name, f"{last}, {first}"
    raise RuntimeError(f"ran out of names in {region['id']}")


def _where(c: str) -> str:
    country = corpus.world()["countries"][c]
    return c if country == c else f"{c}, {country}"


def make_artist(rng: random.Random, idx: int, year: int, taken: set[str], profile: str | None = None) -> Artist:
    w = corpus.world()
    region = weighted(rng, w["regions"])
    profile = profile or weighted(rng, PROFILES)["id"]
    heritage = pick(rng, region["heritage"])
    pronoun = rng.choices(["she", "he", "they"], weights=[5, 4, 2])[0]

    if profile == "collective":
        place = _where(pick(rng, region["born"]))
        templates = w["collective_names"] + region.get("collectives", []) * 3
        name = fill(pick(rng, templates), {"place": place, "word": pick(rng, w["collective_words"])})
        if name in taken:
            name = f"{name} ({place})"
        members = [_name(rng, region, taken, reserve=False)[0] for _ in range(rng.randint(3, 5))]
        return Artist(id=f"a{idx:02d}-{slugify(name, 30)}", name=name, sort_name=name.removeprefix("The "),
                      collective=True, pronoun="they", born_year=None, born_place=place, died_year=None,
                      lives=[place], profile=profile, heritage=heritage, members=members, origin=region['id'],
                      founded_year=rng.randint(2008, 2021))

    name, sort_name = _name(rng, region, taken)
    born_place = _where(pick(rng, region["born"]))
    if profile == "rediscovered":
        born = rng.randint(1902, 1948)
        died = min(year - 6, born + rng.randint(38, 88))
        return Artist(id=f"a{idx:02d}-{slugify(name, 30)}", name=name, sort_name=sort_name, collective=False,
                      pronoun=pronoun, born_year=born, born_place=born_place, died_year=died, lives=[],
                      profile=profile, heritage=heritage, origin=region["id"])
    born = {"midcareer": (1974, 1990), "emerging": (1990, 1998), "elder": (1938, 1956)}[profile]
    born_year = rng.randint(*born)
    lives = [born_place] if profile == "elder" or rng.random() < 0.3 else []
    lives = [l for l in lives]
    hubs = ["Berlin", "London", "New York", "Paris", "Amsterdam", "Brussels", "Los Angeles", "Lisbon", "Mexico City"]
    while len(lives) < (1 if profile == "elder" else 2):
        place = _where(pick(rng, region["lives"] + hubs))
        if place not in lives:
            lives.append(place)
    return Artist(id=f"a{idx:02d}-{slugify(name, 30)}", name=name, sort_name=sort_name, collective=False,
                  pronoun=pronoun, born_year=born_year, born_place=born_place, died_year=None, lives=lives,
                  profile=profile, heritage=heritage, origin=region["id"])
