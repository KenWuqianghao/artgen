from __future__ import annotations

import random

from .. import corpus
from ..model import Artist, Work, city
from ..textkit import fill, fix_articles, join_list, pick
from .common import base_slots

JOBS = ["fisherman", "nurse", "bus driver", "tailor", "schoolteacher", "market trader", "mechanic", "cook", "railway clerk"]


def bio(rng: random.Random, a: Artist, w: Work, year: int) -> str:
    B = corpus.lexicon()["bio"]
    s = base_slots(a, w)
    s.update({"forms": B["forms"].get(w.family, "sculpture and installation"), "job": pick(rng, JOBS)})
    solo = [fill(v, {"city": c}) for v, c in zip(pick(rng, B["solo_venues"], 2), pick(rng, [city(x) for x in a.lives] or [s["city"]] * 2, 2) * 2)]
    if a.collective:
        s.update({"members": join_list(a.members), "group1": pick(rng, B["group_events"]), "group2": pick(rng, B["group_events"])})
        return fix_articles(fill(B["collective"][0], s))
    if a.died_year:
        lo = max((a.died_year or 2000) + 2, 2008)
        s.update({"solo1": solo[0], "year_retro": rng.randint(min(lo, year - 1), year - 1)})
        return fix_articles(fill(pick(rng, B["deceased"]), s))
    lives = " and ".join(city(x) for x in a.lives)
    first = f"{a.name} (b. {a.born_year}, {s['city']}) lives and works in {lives}."
    practice = fill(pick(rng, B["practice"]), s)
    y1, y2 = sorted(rng.sample(range(year - 6, year), 2), reverse=True)
    groups = pick(rng, B["group_events"], 2)
    shows = f"Recent solo exhibitions include {solo[0]} ({y1}) and {solo[1]} ({y2}). {a.pronoun.capitalize()} {'have' if a.pronoun == 'they' else 'has'} participated in {groups[0]} and {groups[1]}."
    if a.profile == "emerging":
        shows = f"{a.pronoun.capitalize()} recently completed a residency at {pick(rng, B['residencies'])}, and this is {s['poss']} first biennial."
    return fix_articles(" ".join([first, practice, shows]))
