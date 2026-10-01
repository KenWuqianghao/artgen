"""Curatorial statement, section texts, press release and visitor information."""
from __future__ import annotations

import random

from .. import corpus
from ..model import Exhibition
from ..textkit import fill, join_list, number_word, pick


def section_texts(rng: random.Random, sections: list[str], metaphor: dict) -> list[str]:
    lx = corpus.lexicon()
    templates = pick(rng, lx["section_texts"], len(sections))
    return [fill(t, {"section": s, "verb": pick(rng, lx["section_verbs"]), "keyword": pick(rng, metaphor["keywords"])})
            for s, t in zip(sections, templates)]


def statement(rng: random.Random, ex: Exhibition, metaphor: dict, director: str, co: list[str]) -> list[str]:
    lx = corpus.lexicon()
    S = lx["statement"]
    crises = pick(rng, S["crises"], 3)
    slots = {
        "edition_name": ex.edition_name, "title": ex.title, "city": ex.city, "opening": ex.opening, "closing": ex.closing,
        "n_venues": number_word(len(ex.venues)), "director": director, "co": join_list(co), "n_artists": len(ex.artists),
        "n_new": sum(1 for a in ex.artists if not a.died_year), "crisis1": crises[0], "crisis2": crises[1], "crisis3": crises[2],
        "keyword": pick(rng, metaphor["keywords"]), "n_sections": number_word(len(ex.sections)),
        "sections": join_list([s.title for s in ex.sections]), "city_fact": lx["city_facts"].get(ex.city, "water and trade"),
    }
    epigraph = f"> {metaphor['image'][0].upper() + metaphor['image'][1:]}. ({ex.title_source})"
    paras = [
        fill(S["announce"], slots),
        ex.title_source,
        f"{metaphor['concept']} {fill(pick(rng, S['not_this']), slots)}",
        fill(pick(rng, S["crisis"]), slots),
        fill(pick(rng, S["method"]), slots),
    ]
    for s in ex.sections:
        names = [ex.artist(w.artist_id).name for w in ex.works_in(s.id)][:3]
        if names:
            paras.append(f"*{s.title}*. {s.text} It includes work by {join_list(names)}.")
    paras += [fill(S["place"], slots), pick(rng, S["modesty"]), pick(rng, S["closing"])]
    del epigraph
    return paras


def press_release(rng: random.Random, ex: Exhibition, director: str, co: list[str]) -> list[str]:
    P = corpus.lexicon()["press"]
    countries = {a.born_place.rsplit(", ", 1)[-1] for a in ex.artists if a.born_place}
    picks = pick(rng, [w for w in ex.works if w.media_kind != "x"], 3)
    highlights = join_list([f"{ex.artist(w.artist_id).name}'s {w.form.lower()} *{w.title}*" for w in picks])
    slots = {"institution": ex.institution[0].upper() + ex.institution[1:], "edition_name": ex.edition_name, "title": ex.title,
             "director": director, "co": join_list(co), "opening": ex.opening, "closing": ex.closing,
             "n_venues": number_word(len(ex.venues)), "city": ex.city, "n_artists": len(ex.artists), "n_countries": len(countries),
             "highlights": highlights, "quote": pick(rng, P["director_quotes"]).rstrip(".") + ","}
    return [fill(P["lead"], slots)] + [fill(b, slots) for b in P["body"][:2]] + [fill(P["quote"], slots)] + [fill(b, slots) for b in P["body"][2:]]


def visitor_info(ex: Exhibition) -> list[str]:
    return list(corpus.lexicon()["visitor_info"])
