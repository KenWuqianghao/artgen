from __future__ import annotations

from ..model import Artist, Work, city

POSS = {"she": "her", "he": "his", "they": "their"}


def surname(a: Artist) -> str:
    if a.collective:
        return a.name
    return a.sort_name.split(",")[0]


def poss(a: Artist) -> str:
    return POSS[a.pronoun]


def surname_poss(a: Artist) -> str:
    s = surname(a)
    return f"{s}'" if s.endswith("s") else f"{s}'s"


def italic(title: str) -> str:
    return f"*{title}*"


def base_slots(a: Artist, w: Work) -> dict:
    m = w.materials
    return {
        "name": a.name, "surname": surname(a), "surname_poss": surname_poss(a), "poss": poss(a), "poss_cap": poss(a).capitalize(),
        "pron": a.pronoun, "pron_cap": a.pronoun.capitalize(), "city": city(a.born_place or ""), "heritage": a.heritage,
        "title": italic(w.title), "m1": m[0], "m2": m[1] if len(m) > 1 else m[0], "m1_last": m[0].split()[-1],
        "born_year": a.born_year, "died_year": a.died_year, "founded_year": a.founded_year,
        "member_count": len(a.members) or 4, "form_lower": w.form.lower(),
        "t1": w.themes[0] if w.themes else "memory", "t2": w.themes[1] if len(w.themes) > 1 else "care",
    }
