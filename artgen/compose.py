"""Compose a random artwork specification from the knowledge base."""
import random
import re
from .data import load

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]


def cap(s):
    return s[0].upper() + s[1:] if s else s


def title_case(s):
    small = {"a", "an", "the", "of", "for", "and", "in", "on", "to", "as", "is", "at", "by"}
    words = s.split()
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        if i > 0 and lw in small:
            out.append(lw)
        else:
            out.append(cap(w))
    return " ".join(out)


def to_infinitive(verb):
    # "gestures toward" -> "Gesture Toward"; "destabilises" -> "Destabilise"
    head, *rest = verb.split(" ")
    if head.endswith("ies"):
        head = head[:-3] + "y"
    elif head.endswith("sses") or head.endswith("shes") or head.endswith("ches") or head.endswith("xes"):
        head = head[:-2]
    elif head.endswith("s"):
        head = head[:-1]
    return title_case(" ".join([head] + rest))


def base_verb(verb):
    """'destabilises' -> 'destabilise'; 'gestures toward' -> 'gesture toward'."""
    head, *rest = verb.split(" ")
    if head.endswith("ies"):
        head = head[:-3] + "y"
    elif head.endswith(("sses", "shes", "ches", "xes")):
        head = head[:-2]
    elif head.endswith("s"):
        head = head[:-1]
    return " ".join([head] + rest)


def fix_articles(s):
    s = re.sub(r"\bA ([AEIOUaeiou])", r"An \1", s)
    s = re.sub(r"\ba ([AEIOUaeiou])", r"an \1", s)
    return s


def to_gerund(verb):
    head, *rest = verb.split(" ")
    if head.endswith("ies"):
        head = head[:-3] + "ying"
    elif head.endswith("es") and head[-3] in "sxh":
        head = head[:-2] + "ing"
    elif head.endswith("s"):
        head = head[:-1]
        if head.endswith("e") and not head.endswith("ee"):
            head = head[:-1]
        head += "ing"
    return title_case(" ".join([head] + rest))


def plural(noun):
    last = noun.split()[-1]
    if last.endswith("s"):
        return noun
    if last.endswith("y") and last[-2] not in "aeiou":
        return noun[:-1] + "ies"
    return noun + "s"


def fill_technique(t, rng, materials, exclude):
    if "{material}" in t:
        pool = [m for m in materials if m not in exclude]
        return t.replace("{material}", rng.choice(pool))
    return t


def compose(seed=None, kind=None):
    """Return a dict describing one artwork. `kind` may be 'video' or 'installation'."""
    rng = random.Random(seed)
    d = load()

    forms = d["forms"]
    if kind:
        forms = [f for f in forms if f["kind"] == kind]
    form = rng.choice(forms)

    n_materials = rng.choice([2, 3, 3, 4])
    materials = rng.sample(d["materials"], n_materials)
    technique = fill_technique(rng.choice(d["techniques"]), rng, d["materials"], materials)

    theme = rng.choice(d["themes"])
    theme2 = rng.choice([t for t in d["themes"] if t is not theme])
    keyword = rng.choice(theme["keywords"])
    keyword2 = rng.choice(theme2["keywords"])
    theorists = rng.sample(d["theorists"], 3)
    theorist = theorists[0]
    theorist_last = theorist["name"].split(" and ")[0].split()[-1]

    noun = rng.choice(d["nouns"])
    adjective = rng.choice(d["adjectives"])
    verb = rng.choice(d["verbs"])
    foreign = rng.choice(d["foreign_words"])
    number = rng.choice([7, 12, 40, 99, 108, 340, 1000, 1948, 2000])

    def kw_cap(k):
        return title_case(re.sub(r"^the ", "", k))

    ctx = {
        "keyword": re.sub(r"^the ", "", keyword),
        "keyword_cap": kw_cap(keyword),
        "keyword2_cap": kw_cap(keyword2),
        "noun_cap": title_case(noun),
        "adjective_cap": title_case(adjective),
        "theorist_last": theorist_last,
        "verb_inf": to_infinitive(verb),
        "verb_gerund": to_gerund(verb),
        "material": materials[0],
        "material_cap": title_case(materials[0]),
        "material_cap_plural": title_case(plural(materials[0])),
        "roman": rng.choice(ROMAN),
        "foreign_word": foreign["word"],
        "translation": foreign["translation"],
        "number": number,
    }
    title = fix_articles(rng.choice(d["title_templates"]).format(**ctx))

    is_collective = rng.random() < 0.15
    if is_collective:
        artist = rng.choice(d["collectives"])
    else:
        artist = f"{rng.choice(d['artist_first_names'])} {rng.choice(d['artist_last_names'])}"

    city_a, city_b = rng.sample(d["cities"], 2)
    year = rng.choice([2024, 2025, 2025, 2026, 2026, 2026])
    birth_year = rng.randint(1974, 1996)

    if form["kind"] == "video":
        channels = rng.choice(form.get("channels", [1]))
        minutes = rng.randint(4, 47)
        seconds = rng.randint(0, 59)
        duration = f"{minutes}'{seconds:02d}\""
        motifs = rng.sample(d["video_motifs"], 3)
        motifs = [fill_technique(m, rng, d["materials"], []) for m in motifs]
        ch = "single-channel" if channels == 1 else f"{channels}-channel"
        dims = f"{ch} {'colour' if rng.random() < 0.7 else 'black-and-white'} video, {'sound' if rng.random() < 0.8 else 'silent'}, {duration}, loop"
    else:
        channels = None
        duration = None
        motifs = []
        dims = rng.choice(["dimensions variable", f"{rng.randint(180, 900)} × {rng.randint(200, 1400)} × {rng.randint(120, 600)} cm", "dimensions variable; site-specific"])

    spec = {
        "seed": seed,
        "title": title,
        "artist": artist,
        "is_collective": is_collective,
        "artist_birth_year": None if is_collective else birth_year,
        "artist_birthplace": rng.choice(d["birthplaces"]),
        "artist_cities": [city_a, city_b],
        "year": year,
        "form": form["name"],
        "kind": form["kind"],
        "channels": channels,
        "duration": duration,
        "dimensions": dims,
        "materials": materials,
        "technique": technique,
        "video_motifs": motifs,
        "theme": theme["name"],
        "theme_secondary": theme2["name"],
        "keyword": keyword,
        "keyword_secondary": keyword2,
        "theorists": theorists,
        "noun": noun,
        "adjective": adjective,
        "verb": verb,
        "adverb": rng.choice(d["adverbs"]),
        "adverb2": rng.choice(d["adverbs"]),
        "venue": rng.choice(d["venues"]),
        "gallery": rng.choice(d["galleries"]),
        "funder": rng.choice(d["funders"]),
        "biennials": rng.sample(d["biennials"], 2),
        "residency": rng.choice(d["residencies"]),
        "epigraph": rng.choice(d["epigraphs"]),
        "photo_style": rng.choice(d["photo_styles"]),
        "video_style": rng.choice(d["video_styles"]),
        "curator": f"{rng.choice(d['artist_first_names'])} {rng.choice(d['artist_last_names'])}",
        "curator_title": rng.choice(d["curator_titles"]).replace("{city}", rng.choice(d["cities"])),
        "foreign": foreign,
        "_rng_state": rng.random(),
    }
    return spec
