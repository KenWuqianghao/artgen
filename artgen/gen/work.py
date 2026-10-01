"""Generate one artwork from an archetype, coherent with its artist and venue."""
from __future__ import annotations

import random

from .. import corpus
from ..model import Artist, Venue, Work, city
from ..textkit import cap, fill, fix_articles, join_list, number_word, pick, sentence_case, slugify, weighted
from .title import make_title

COLOURS = ["indigo", "ochre", "rust red", "pale blue", "saffron", "bone white", "deep green", "faded pink", "charcoal", "turquoise"]
HERITAGE_HINTS = {  # artist heritage keyword -> archetype families it pulls towards
    "weav": ["textile"], "quilt": ["textile"], "embroider": ["textile"], "stitch": ["textile"], "dye": ["textile"], "batik": ["textile"],
    "lace": ["textile"], "kantha": ["textile"], "cloth": ["textile"], "bead": ["textile", "figure"], "mas ": ["textile", "performance"],
    "pott": ["ceramic"], "terracotta": ["ceramic"], "clay": ["ceramic"], "onggi": ["ceramic"], "tile": ["ceramic", "architecture"],
    "paint": ["painting"], "mural": ["painting"], "print": ["painting"], "lacquer": ["painting"], "song": ["sound"], "music": ["sound"],
    "polyphon": ["sound"], "qawwali": ["sound"], "maqam": ["sound"], "joik": ["sound"], "radio": ["sound", "archive"],
    "mine": ["found", "earth"], "mill": ["found"], "factory": ["found"], "shipyard": ["found"], "plantation": ["earth", "archive"],
    "garden": ["earth"], "harvest": ["earth"], "rice": ["earth"], "herb": ["earth", "scent"], "coffee": ["scent"], "spice": ["scent"],
    "archive": ["archive"], "market": ["found", "archive"], "shop": ["found", "archive"], "ritual": ["shrine"], "church": ["shrine", "painting"],
    "shaman": ["shrine"], "candom": ["shrine", "textile"], "vodou": ["shrine", "textile"], "carving": ["figure"], "stone": ["figure"],
}
DIM_DEFAULTS = {"h": (180, 420), "w": (200, 900), "d": (120, 500), "h_small": (40, 120), "w_big": (900, 2400), "d_big": (600, 1400), "w_m": (6, 14)}
JOBS = ["fisherman", "nurse", "bus driver", "tailor", "schoolteacher", "market trader", "mechanic", "cook"]


def _family_bias(artist: Artist) -> dict[str, float]:
    bias: dict[str, float] = {}
    h = artist.heritage.lower()
    for key, fams in HERITAGE_HINTS.items():
        if key in h:
            for f in fams:
                bias[f] = 3.0
    if artist.profile in ("rediscovered", "elder"):
        bias["painting"] = max(bias.get("painting", 1), 2.5)
        bias["textile"] = max(bias.get("textile", 1), 2.0)
        for f in ("video", "digital", "light", "architecture", "performance", "scent"):
            bias[f] = 0.0 if artist.profile == "rediscovered" else 0.2
    if artist.collective:
        for f in ("archive", "architecture", "textile", "found"):
            bias[f] = max(bias.get(f, 1), 2.0)
    return bias


def pick_archetype(rng: random.Random, artist: Artist, families: list[str] | None = None, avoid: set[str] = frozenset()) -> dict:
    bias = _family_bias(artist)
    pool = [a for a in corpus.archetypes() if (not families or a["family"] in families) and a["id"] not in avoid
            and (artist.profile != "rediscovered" or a.get("historical"))]
    if not pool:
        pool = [a for a in corpus.archetypes() if artist.profile != "rediscovered" or a.get("historical")]
    weights = [a["weight"] * bias.get(a["family"], 1.0) for a in pool]
    return rng.choices(pool, weights=weights, k=1)[0]


PRESENT_WORDS = ("present", "last year", " now", "will be", "is due", "since it opened", "still operate", "today")


def _year_then(rng: random.Random, artist: Artist) -> int:
    if artist.died_year and artist.born_year:
        return rng.randint(artist.born_year + 18, artist.died_year - 2)
    return rng.choice([1948, 1956, 1967, 1975, 1982, 1994, 2001, 2008, 2014])


def for_variant(texts: list[str], k: int) -> list[str]:
    """Keep untagged sentences and those tagged for scene variant k ('<k>|text'); strip the tags."""
    out = []
    for t in texts:
        if len(t) > 2 and t[0].isdigit() and t[1] == "|":
            if int(t[0]) == k:
                out.append(t[2:])
        else:
            out.append(t)
    return out


def _fact(rng: random.Random, arch: dict, artist: Artist, slots: dict) -> str:
    facts = arch["facts"]
    if artist.died_year:
        facts = [f for f in facts if not any(w in f for w in PRESENT_WORDS)] or [
            "The work was made in {year_then} and shown only once during the artist's lifetime, in a church hall in {place}."]
    return fix_articles(fill(pick(rng, facts), slots))


def _materials(rng: random.Random, arch: dict, pool: dict | None = None) -> tuple[list[str], list[str]]:
    m = pool or arch["materials"]
    core = pick(rng, m["core"], rng.randint(*m["core_n"]))
    accent_pool = [x for x in m.get("accent", []) if x not in core]
    accent = pick(rng, accent_pool, rng.randint(*m["accent_n"])) if accent_pool and m["accent_n"][1] else []
    return core, accent


def _slots(rng: random.Random, arch: dict, artist: Artist, core: list[str], accent: list[str], year: int) -> dict:
    mats = core + accent
    count = rng.choice(arch["slots"].get("count", [7, 12, 24, 40]))
    s = {
        "m1": mats[0], "m2": mats[1] if len(mats) > 1 else mats[0], "m3": mats[2] if len(mats) > 2 else (mats[-1]),
        "count": count,
        "n": rng.choice([4, 6, 9, 12, 17, 23, 30, 40, 62]), "months": rng.choice([3, 4, 6, 8, 10, 14, 18]),
        "minutes": rng.randint(6, 48), "seconds": rng.randint(0, 59), "hours": rng.choice([3, 6, 9, 11, 14, 20]),
        "year_then": _year_then(rng, artist),
        "place": city(artist.born_place or ""), "heritage": artist.heritage, "colour": pick(rng, COLOURS),
        "small": f"{rng.randint(18, 40)} × {rng.randint(14, 32)}", "age_start": rng.randint(41, 66),
        "years_work": rng.randint(12, 35), "job": pick(rng, JOBS),
        "Accents": join_list(accent).lower() if accent else "seating",
        "phrase": pick(rng, corpus.lexicon()["phrases"]),
    }
    for k, (lo, hi) in DIM_DEFAULTS.items():
        s[k] = rng.randint(lo, hi)
    s["count_word"] = number_word(count) if count <= 12 else str(count)
    return s


def _medium(rng: random.Random, arch: dict, core: list[str], accent: list[str], slots: dict) -> str:
    materials = cap(join_list(core + accent, conj="and"))
    if "{Materials}" in arch["medium"]:
        line = arch["medium"].replace("{Materials}", ", ".join([cap(core[0])] + core[1:] + accent))
    else:
        line = fill(arch["medium"], slots)
    for extra in arch.get("extras", []):
        if rng.random() < extra["p"]:
            line += ", " + fill(extra["text"], slots)
    del materials
    return line


def make_work(rng: random.Random, idx: int, artist: Artist, venue: Venue, section_id: str, year: int, edition_name: str,
              arch: dict | None = None, used_titles: set | None = None) -> Work:
    w = corpus.world()
    arch = arch or pick_archetype(rng, artist, venue_families(venue))
    k = rng.randrange(len(arch["scenes"]))
    variant = arch["scenes"][k]
    arch = {**arch, **{f: for_variant(arch.get(f, []), k) for f in ("facts", "process", "turns", "quotes", "change")}}
    scene_t, pool = (variant["t"], variant["materials"]) if isinstance(variant, dict) else (variant, None)
    core, accent = _materials(rng, arch, pool)
    need = 3 if "{m3}" in scene_t else 2 if "{m2}" in scene_t else 1
    spare = [x for x in (pool or arch["materials"])["core"] + (pool or arch["materials"]).get("accent", []) if x not in core + accent]
    while len(core) + len(accent) < need and spare:
        accent.append(spare.pop(rng.randrange(len(spare))))
    slots = _slots(rng, arch, artist, core, accent, year)
    scene = sentence_case(fix_articles(fill(scene_t, slots)))
    title = make_title(rng, origin=artist.origin, place=city(artist.born_place or "") or "the river", material=core[0], year=year, used=used_titles)
    work_year = year if artist.died_year is None else rng.randint((artist.born_year or 1920) + 25, artist.died_year)
    if artist.died_year is None and rng.random() < 0.25:
        work_year = f"{year - rng.randint(1, 4)}–{str(year)[2:]}"
    dims = fill(pick(rng, arch["dimensions"]), slots)
    country = (artist.born_place or "Italy").rsplit(", ", 1)[-1]
    support = f"Produced with the support of {fill(pick(rng, w['funders']), {'country': country})}"
    if artist.died_year:
        courtesy = f"Courtesy the Estate of {artist.name} and {pick(rng, w['galleries'])}"
        support = f"Lent by {pick(rng, ['a private collection', 'the family of the artist', 'a national museum'])}"
    elif artist.collective:
        courtesy = "Courtesy the collective"
    else:
        courtesy = f"Courtesy the artist and {pick(rng, w['galleries'])}"
    if artist.died_year is None:
        support = f"Commissioned by the {edition_name}. {support}"
    return Work(
        id=f"w{idx:02d}", slug=f"{idx:02d}-{slugify(title, 48)}", artist_id=artist.id, title=title, year=work_year,
        archetype=arch["id"], family=arch["family"], kind=arch["kind"], form=arch["form"],
        medium=_medium(rng, arch, core, accent, slots), dimensions=dims, scene=scene,
        materials=core + accent, nonvisual=[e["text"] for e in arch.get("extras", [])],
        themes=list(arch["themes"]), references=[], claims=[fix_articles(fill(t, slots)) for t in arch["turns"]] or ["The work leaves the visitor with more questions than it answers."],
        venue_id=venue.id, section_id=section_id, courtesy=courtesy, support=support,
        photo_credit=pick(rng, w["photographers"]),
        extra={
            "fact": _fact(rng, arch, artist, slots),
            "process": fix_articles(fill(pick(rng, arch["process"]), slots)) if arch["process"] else "",
            "quote": pick(rng, arch["quotes"]) if arch["quotes"] else "I made it because nobody else would.",
            "change": fix_articles(fill(pick(rng, arch["change"]), slots)) if arch.get("change") else "",
            "interaction": pick(rng, arch["interaction"]) if arch.get("interaction") else "",
            "camera": arch["camera"], "people_p": arch["people_p"], "basis": arch["basis"],
        },
    )


def venue_families(venue: Venue) -> list[str]:
    return venue.families
