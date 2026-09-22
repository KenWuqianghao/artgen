"""Template-based generation of wall label, artist statement and curatorial essay.

The register is International Art English (Rule & Levine, 2012): adverb + verb pairs,
nominalised abstractions, paired near-synonyms, and a refusal to conclude.
"""
import random
import re
from .data import load
from .compose import base_verb


def _rng(spec):
    return random.Random(f"{spec.get('seed')}-text-{spec['title']}")


def _kw(k):
    return re.sub(r"^the ", "", k)


def _and_list(items):
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def _last(name):
    return name.split(" and ")[0].split()[-1]


def wall_label(spec):
    """The short label next to the work."""
    lines = [f"**{spec['artist']}**"]
    if spec["is_collective"]:
        lines.append(f"Founded {spec['artist_birth_year'] or 2019}. Based between {spec['artist_cities'][0]} and {spec['artist_cities'][1]}.")
    else:
        lines.append(f"b. {spec['artist_birth_year']}, {spec['artist_birthplace']}. Lives and works between {spec['artist_cities'][0]} and {spec['artist_cities'][1]}.")
    lines.append("")
    lines.append(f"*{spec['title']}*, {spec['year']}")
    lines.append(spec["form"].capitalize())
    lines.append(_and_list(spec["materials"]).capitalize())
    lines.append(spec["dimensions"].capitalize())
    lines.append("")
    lines.append(f"Courtesy of the artist and {spec['gallery']}. Commissioned by La Biennale di Venezia with the support of {spec['funder']}.")
    return "\n".join(lines)


def artist_statement(spec):
    rng = _rng(spec)
    d = load()
    t = spec["theorists"]
    m = spec["materials"]
    kw = spec["keyword"]
    kw2 = spec["keyword_secondary"]
    noun2 = rng.choice(d["nouns"])
    adj2 = rng.choice(d["adjectives"])
    verb2 = rng.choice(d["verbs"])

    if spec["kind"] == "video":
        screens = "On a single screen" if spec["channels"] == 1 else f"Across {spec['channels']} screens"
        body_material = (
            f"{screens}, the work moves between {spec['video_motifs'][0]}, "
            f"{spec['video_motifs'][1]}, and {spec['video_motifs'][2]}. Nothing is explained."
        )
    else:
        body_material = (
            f"{spec['composition'][0].upper() + spec['composition'][1:]}. "
            f"The {m[0].split()[-1]} is not a metaphor. It is {m[0]}."
        )

    paras = [
        f"*{spec['title']}* {spec['adverb']} {spec['verb']} the {spec['adjective']} {spec['noun']} of {kw}. "
        f"Working {spec['adverb2']} with {_and_list(m)}, {spec['artist']} asks what it might mean to {base_verb(spec['verb'])} "
        f"{kw} not as an object of knowledge but as a {noun2} to be lived with.",

        body_material,

        f"The work draws on {t[0]['name']}'s notion of {t[0]['concept']} and {t[1]['name']}'s account of {t[1]['concept']}, "
        f"while refusing the {adj2} closure that either might imply. Between {kw} and {kw2}, a third term emerges, "
        f"one that {verb2} rather than names. In this way the work {spec['claim'].replace('{adjective}', spec['claim_adjective'])}.",

        f"Rather than offering resolution, the work holds open a space of {spec['noun']} in which the viewer is invited "
        f"to sit with what cannot be {rng.choice(['resolved', 'translated', 'repaired', 'seen', 'owned', 'counted'])}. "
        f"It is, finally, a proposition about {spec['theme']}: {rng.choice(['tender', 'unfinished', 'porous', 'insistent', 'minor'])}, "
        f"{rng.choice(['and', 'and therefore', 'and perhaps'])} {rng.choice(['necessary', 'impossible', 'ongoing', 'shared'])}.",
    ]
    return "\n\n".join(paras)


def essay(spec):
    """A ~700-word curatorial essay with footnotes."""
    rng = _rng(spec)
    d = load()
    t = spec["theorists"]
    m = spec["materials"]
    kw = spec["keyword"]
    kw2 = spec["keyword_secondary"]
    theorist_last = _last(t[0]["name"])
    fmt = {
        "venue": spec["venue"], "material": m[0], "title": f"*{spec['title']}*", "keyword": _kw(kw),
        "keyword_word": _kw(kw).split()[-1], "artist": spec["artist"], "theme": spec["theme"],
        "noun": spec["noun"], "theorist_last": theorist_last,
    }
    opener = rng.choice(d["essay_openers"]).format(**fmt)
    pivot = rng.choice(d["essay_pivots"]).format(**fmt)
    closer = rng.choice(d["essay_closers"]).format(**fmt)

    verbs = rng.sample(d["verbs"], 4)
    adjs = rng.sample(d["adjectives"], 4)
    nouns = rng.sample(d["nouns"], 4)
    advs = rng.sample(d["adverbs"], 3)
    pages = [rng.randint(3, 240) for _ in range(4)]

    if spec["kind"] == "video":
        sound = rng.choice(['a low hum', 'a woman breathing', 'the shipping forecast', 'wind over a microphone', 'a lullaby sung out of tune'])
        if spec["channels"] == 1:
            description = (
                f"Projected onto a single wall in {spec['venue']}, {fmt['title']} runs for {spec['duration']} and loops without announcement. "
                f"We see {spec['video_motifs'][0]}; then, without transition, {spec['video_motifs'][1]}. Near the end, {spec['video_motifs'][2]}. "
                f"The cuts are not motivated. They simply happen, so that the work is never quite where one left it. "
                f"Sound arrives from behind the viewer, unattached to any image: {sound}."
            )
        elif spec["channels"]:
            description = (
                f"Installed across {spec['channels']} screens in {spec['venue']}, {fmt['title']} runs for {spec['duration']} and loops without announcement. "
                f"On one screen, {spec['video_motifs'][0]}; on another, {spec['video_motifs'][1]}. A third shows {spec['video_motifs'][2]}. "
                f"The channels are not synchronised. They drift, meet, and part again, so that the work is never the same work twice. "
                f"Sound arrives from a fourth position, unattached to any image: {sound}."
            )
    elif spec["kind"] == "painting":
        description = (
            f"In {spec['venue']}, {spec['artist']} shows {spec['composition']}. The medium is {m[0]}"
            f"{(' with ' + _and_list(m[1:])) if len(m) > 1 else ''}. "
            f"The style is {rng.choice(['deliberately naive', 'a modernist pastiche', 'flat and crowded to the edges', 'unhurried', 'closer to a diagram than a picture'])}; "
            f"the subject is {rng.choice(['everyday life', 'the artist\'s family', 'plants', 'two bodies', 'a village that no longer exists', 'nothing in particular'])}. "
            f"One could call it painting. The wall text prefers not to."
        )
    else:
        description = (
            f"In {spec['venue']}, {spec['artist']} has installed {spec['composition']}. The materials are {_and_list(m)}. "
            f"The scale is {rng.choice(['modest', 'overwhelming', 'deceptively domestic', 'architectural'])}; the light is {rng.choice(['withheld', 'borrowed from the street', 'a single bare bulb', 'the colour of weak tea'])}. "
            f"There is a temptation to walk quickly. The work {advs[0]} resists this. {m[1].capitalize()} {rng.choice(['catches on the shoe.', 'gives off a faint smell of the sea.', 'reflects the visitor back as a stranger.', 'has been left to settle.', 'smells faintly of burnt sugar.', 'asks for nothing in particular.'])}"
        )

    paras = [
        f"> {spec['epigraph']}",
        "",
        opener,
        "",
        description,
        "",
        f"It is important to say what the work is not. It is not an illustration of {spec['theme']}, though {spec['theme']} is everywhere in it. "
        f"It is not a monument, though it {verbs[0]} the grammar of the monument. And it is not, despite the {m[0]}, about {m[0].split()[-1]}. "
        f"{spec['artist']} {advs[1]} {verbs[1]} the {adjs[0]} {nouns[0]} of {kw}, treating it less as a subject than as a {rng.choice(['method', 'weather', 'companion', 'wound', 'score'])}. "
        f"The wall text tells us that the work {spec['claim'].replace('{adjective}', spec['claim_adjective'])}. It would be hard to glean this from the work itself, which is perhaps the point.[^1]",
        "",
        f"{pivot} {theorist_last} writes of {t[0]['concept']} as that which {rng.choice(['cannot be reduced to transparency', 'escapes the archive', 'lives in the gap between languages', 'refuses to be counted', 'persists after the event'])}.[^2] "
        f"{fmt['title']} takes this seriously. Its {adjs[1]} {nouns[1]} is not a failure of communication but a {rng.choice(['strategy', 'gift', 'form of care', 'refusal', 'kind of hospitality'])}. "
        f"To stand before it is to be {advs[2]} reminded that {kw} and {kw2} are not opposites but {rng.choice(['neighbours', 'siblings', 'the same wound seen from two sides', 'two tempos of one song'])}.",
        "",
        f"There is a longer history here. {_last(t[1]['name'])}'s account of {t[1]['concept']} reminds us that {rng.choice(['the body remembers what the state forgets', 'every ruin is also a construction site', 'the margin is where the centre goes to be forgiven', 'listening is a political act', 'to repair is not to restore'])}.[^3] "
        f"{spec['artist']} inherits this thinking but {rng.choice(['bends', 'slows', 'localises', 'un-writes', 'softens'])} it. Where {_last(t[1]['name'])} theorises, the work {verbs[2]}. "
        f"Where the institution demands legibility, the work offers {nouns[2]}: {adjs[2]}, {adjs[3]}, and {rng.choice(['unhurried', 'uninsured', 'unpaid', 'untranslated', 'unrepentant'])}.",
        "",
        f"One might object that such {nouns[3]} risks {rng.choice(['aestheticising suffering', 'a certain preciousness', 'becoming its own institution', 'speaking only to those already listening'])}. "
        f"The objection is fair, and the work knows it. This is why the {m[-1]} matters: it is {rng.choice(['cheap', 'ordinary', 'perishable', 'stolen', 'borrowed', 'unbeautiful'])}, and it will {rng.choice(['not survive the exhibition', 'be returned', 'be thrown away in November', 'outlive us all', 'go back to the sea'])}. "
        f"{_last(t[2]['name'])} might call this {t[2]['concept']}.[^4] {spec['artist']} does not call it anything.",
        "",
        closer,
        "",
        "---",
        "",
        f"[^1]: See {spec['artist']} in conversation with the author, {spec['artist_cities'][0]}, {rng.choice(['March', 'October', 'January', 'June'])} {spec['year'] - 1}.",
        f"[^2]: {t[0]['name']}, *{t[0]['work']}* ({t[0]['year']}), p. {pages[0]}.",
        f"[^3]: {t[1]['name']}, *{t[1]['work']}* ({t[1]['year']}), pp. {pages[1]}–{pages[1] + rng.randint(2, 19)}.",
        f"[^4]: {t[2]['name']}, *{t[2]['work']}* ({t[2]['year']}), p. {pages[2]}. The term is used here loosely, as the author would no doubt object.",
        "",
        f"*{spec['curator']} is {spec['curator_title']}.*",
    ]
    return "\n".join(paras)


def bio(spec):
    rng = _rng(spec)
    if spec["is_collective"]:
        who = f"{spec['artist']} is a collective working between {spec['artist_cities'][0]} and {spec['artist_cities'][1]}."
    else:
        who = (f"{spec['artist']} (b. {spec['artist_birth_year']}, {spec['artist_birthplace']}) lives and works between "
               f"{spec['artist_cities'][0]} and {spec['artist_cities'][1]}.")
    return (
        f"{who} Their practice spans {spec['form'].split(' (')[0]}, {rng.choice(['writing', 'sound', 'pedagogy', 'gardening', 'cooking', 'radio'])} and "
        f"{rng.choice(['long-term collaboration with communities', 'the reactivation of neglected archives', 'the study of vernacular building', 'forms of collective listening'])}. "
        f"Recent presentations include {spec['biennials'][0]} and {spec['biennials'][1]}. They were a resident at {spec['residency']} and "
        f"are represented by {spec['gallery']}."
    )
