"""Catalogue essays: this is where the theory lives, as it does in real catalogues."""
from __future__ import annotations

import random

from .. import corpus
from ..model import Artist, Venue, Work
from ..textkit import cap, fill, fix_articles, join_list, pick
from .common import base_slots, surname


def _short(t: dict) -> str:
    return t.get("short") or t["name"].split()[-1]


def essay(rng: random.Random, a: Artist, w: Work, venue: Venue, edition_name: str, author: str, jargon: int = 2) -> tuple[str, list[str], str]:
    """Returns (essay markdown with [^n] notes after a '---' line, references used, author line)."""
    E = corpus.lexicon()["essay"]
    thinkers = pick(rng, corpus.world()["theorists"], 3)
    t0, t1, t2 = thinkers
    s = base_slots(a, w)
    theme = w.themes[0] if w.themes else "memory"
    s.update({"venue": venue.name, "theme": theme, "theorist_last": _short(t0)})
    v = pick(rng, E["verbs"], 4)
    adj = pick(rng, E["adjectives"], 5)
    nn = pick(rng, E["nouns"], 4)
    adv = pick(rng, E["adverbs"], 3)
    sn = surname(a)
    pages = [rng.randint(3, 240) for _ in range(3)]
    paras = [
        fill(pick(rng, E["openers"]), s),
        f"The materials are modest: {join_list(w.materials[:3]).lower()}. {w.extra.get('process', '')} "
        f"The {s['m1_last']} is not a metaphor. It is {s['m1']}.",
        f"It is important to say what the work is not. It is not an illustration of {theme}, though {theme} is everywhere in it. "
        f"It is not a monument, though it {v[0]} the grammar of the monument. {sn} {adv[0]} {v[1]} the {adj[0]} {nn[0]} of {s['m1']}, "
        f"treating it less as a subject than as a {pick(rng, ['method', 'weather', 'companion', 'score', 'wound'])}.[^1]",
        f"{fill(pick(rng, E['pivots']), s)} {_short(t0)} writes of {t0['concept']} as that which "
        f"{pick(rng, ['cannot be reduced to transparency', 'escapes the archive', 'lives in the gap between languages', 'refuses to be counted', 'persists after the event'])}.[^2] "
        f"{s['title']} takes this seriously. Its {adj[1]} {nn[1]} is not a failure of communication but a "
        f"{pick(rng, ['strategy', 'gift', 'form of care', 'refusal', 'kind of hospitality'])}.",
        f"There is a longer history here. {_short(t1)}'s account of {t1['concept']} reminds us that "
        f"{pick(rng, ['the body remembers what the state forgets', 'every ruin is also a construction site', 'the margin is where the centre goes to be forgiven', 'listening is a political act', 'to repair is not to restore'])}.[^3] "
        f"{sn} inherits this thinking but {pick(rng, ['bends', 'slows', 'localises', 'softens', 'composts'])} it. Where {_short(t1)} theorises, the work {v[2]}. "
        f"Where the institution demands legibility, the work offers {nn[2]}: {adj[2]}, {adj[3]}, and {pick(rng, ['unhurried', 'uninsured', 'untranslated', 'unfinished'])}.",
        f"One might object that such {nn[3]} risks {pick(rng, ['aestheticising suffering', 'a certain preciousness', 'becoming its own institution', 'speaking only to those already listening'])}. "
        f"The objection is fair, and the work knows it. {_short(t2)} might call this {t2['concept']}.[^4] {sn} does not call it anything.",
        fill(pick(rng, E["closers"]), s),
    ]
    notes = [
        f"[^1]: Conversation between the artist and the author, {s['city'] or 'online'}, {pick(rng, ['March', 'October', 'January', 'June'])} {rng.choice([2024, 2025])}.",
        f"[^2]: {t0['name']}, *{t0['work']}* ({t0['year']}), p. {pages[0]}.",
        f"[^3]: {t1['name']}, *{t1['work']}* ({t1['year']}), pp. {pages[1]}–{pages[1] + rng.randint(2, 19)}.",
        f"[^4]: {t2['name']}, *{t2['work']}* ({t2['year']}), p. {pages[2]}. The term is used here loosely, as the author would no doubt object.",
    ]
    if jargon <= 1:  # plain: keep the description, one theorist, the close
        paras = [paras[0], paras[1], paras[3], paras[-1]]
        notes = [notes[1].replace("[^2]", "[^1]")]
        paras[2] = paras[2].replace("[^2]", "[^1]")
    elif jargon >= 3:  # unbearable: an extra paragraph of stacked theory and two more notes
        x = pick(rng, corpus.world()["theorists"], 2)
        more_adj = pick(rng, E["adjectives"], 4)
        more_n = pick(rng, E["nouns"], 3)
        paras.insert(-1, f"Read alongside {_short(x[0])}'s {x[0]['concept']}[^5] and {_short(x[1])}'s {x[1]['concept']},[^6] "
                         f"the work becomes legible as a {more_adj[0]}, {more_adj[1]} {more_n[0]}: a {more_n[1]} that is at once "
                         f"{more_adj[2]} and {more_adj[3]}, and that {pick(rng, E['adverbs'])} {pick(rng, E['verbs'])} the very {more_n[2]} "
                         f"it appears to {pick(rng, ['index', 'perform', 'withhold', 'metabolise'])}.")
        notes += [f"[^5]: {x[0]['name']}, *{x[0]['work']}* ({x[0]['year']}), p. {rng.randint(3, 240)}.",
                  f"[^6]: {x[1]['name']}, *{x[1]['work']}* ({x[1]['year']}), passim."]
    body = "\n\n".join(fix_articles(cap(p.strip())) for p in paras)
    return body + "\n---\n" + "\n".join(notes), [t["name"] for t in thinkers], author
