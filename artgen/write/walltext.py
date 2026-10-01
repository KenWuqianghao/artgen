"""Wall texts in the plain museum voice the research found: what it is, a sourced fact,
the artist's words, a process detail, a theme sentence with 'explores', a closing turn."""
from __future__ import annotations

import random

from .. import corpus
from ..model import Artist, Work
from ..textkit import cap, fill, fix_articles, pick, spell_small_numbers, with_article
from .common import base_slots


def wall_text(rng: random.Random, a: Artist, w: Work, edition_name: str) -> str:
    lx = corpus.lexicon()
    s = base_slots(a, w)
    s.update({
        "role": pick(rng, lx["roles"].get(w.family, ["artist"])), "form_a": with_article(w.form.lower()),
        "year_then": rng.choice([1979, 1988, 1996, 2003, 2011, 2016]), "country_context": "an international exhibition",
        "verb_inf": pick(rng, lx["verbs_inf"]),
    })
    s["origin_object"] = fill(pick(rng, lx["origin_objects"]), s)
    s["anecdote"] = fill(pick(rng, lx["anecdotes"]), s)
    if a.died_year:
        opener = pick(rng, lx["walltext_open_deceased"])
    elif a.collective:
        opener = pick(rng, lx["walltext_open_collective"])
    else:
        opener = pick(rng, lx["walltext_open"])
    first = fill(opener, s)
    scene = w.scene
    fact = w.extra.get("fact", "")
    q = w.extra.get("quote", "")
    quote = fill(pick(rng, lx["quote_frames"]), {**s, "quote": q, "quote_comma": q[:-1] + "," if q.endswith(".") else q})
    if a.died_year:
        quote = f"A relative remembers {s['pron'] if a.pronoun != 'they' else 'them'} saying: “{w.extra.get('quote', '')}”"
    process = w.extra.get("process", "")
    change = w.extra.get("change", "")
    theme = fill(pick(rng, lx["theme_sentences"]), s)
    turn = pick(rng, w.claims) if w.claims else ""
    interaction = w.extra.get("interaction", "")
    p1 = " ".join(x for x in [first, scene, fact] if x)
    p2 = " ".join(x for x in [quote, process, change, interaction] if x)
    p3 = " ".join(x for x in [theme, turn] if x)
    return "\n\n".join(spell_small_numbers(fix_articles(cap(p))) for p in [p1, p2, p3] if p)
