"""Artwork titles, built from structures observed on recent biennial labels."""
from __future__ import annotations

import random

from .. import corpus
from ..textkit import fix_articles, pick, plural, title_case, weighted


def _data() -> dict:
    return corpus.load("lexicon_titles")


def make_title(rng: random.Random, *, origin: str, place: str, material: str, year: int, used: set | None = None) -> str:
    d = _data()
    words = d["words"].get(origin, [])
    templates = [t for t in d["templates"] if (t.get("needs") != "word" or words) and (used is None or t["t"] not in used)]
    t = weighted(rng, templates, key="w")
    if used is not None:
        used.add(t["t"])
    seen = used or set()
    nouns = pick(rng, [n for n in d["nouns"] if f"noun:{n}" not in seen] or d["nouns"], 3)
    abstract = pick(rng, [n for n in d["abstract"] if f"noun:{n}" not in seen] or d["abstract"])
    word = pick(rng, words) if words else ["", ""]
    first_names = [r["first"] for r in corpus.world()["regions"] if r["id"] == origin] or [corpus.world()["people_first"]]
    n = rng.choice([3, 7, 12, 40, 108, 125, 300])
    slots = {
        "noun": nouns[0], "Noun": title_case(nouns[0]), "Noun2": title_case(nouns[1]), "Noun3": title_case(nouns[2]),
        "Nouns": title_case(plural(nouns[0])), "nouns": plural(nouns[0]), "Nouns2": title_case(plural(nouns[1])),
        "abstract": abstract, "Abstract": title_case(abstract),
        "Adj": title_case(pick(rng, d["adjectives"])), "Body": title_case(pick(rng, d["body"])),
        "verb": pick(rng, d["verbs"]), "place": place, "material": material,
        "name": pick(rng, first_names[0]), "name2": pick(rng, first_names[0]),
        "n": n, "m": n + rng.choice([4, 11, 17]), "month": pick(rng, d["months"]), "day": rng.randint(1, 28),
        "word": word[0], "translation": word[1], "year": year - rng.randint(30, 300),
    }
    title = t["t"]
    if used is not None:
        for k, n in (("{Noun}", nouns[0]), ("{noun}", nouns[0]), ("{Nouns}", nouns[0]), ("{nouns}", nouns[0]), ("{Noun2}", nouns[1]),
                     ("{Nouns2}", nouns[1]), ("{Noun3}", nouns[2]), ("{abstract}", abstract), ("{Abstract}", abstract)):
            if k in title:
                used.add(f"noun:{n}")
    for k, v in slots.items():
        title = title.replace("{" + k + "}", str(v))
    if t.get("case") == "lower":
        title = title.lower() if not t["t"].startswith("{word}") else title
    return fix_articles(title)
