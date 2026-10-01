"""Assemble a whole biennial: edition, title, team, venues, sections, artists, works and all texts."""
from __future__ import annotations

from .. import corpus, __version__
from ..model import Exhibition, Person, Section, Venue, city
from ..prompts import image_prompt
from ..textkit import fill, ordinal, pick, slugify, sub_rng, tidy, weighted
from ..write.bio import bio
from ..write.essay import essay
from ..write.exhibition_texts import press_release, section_texts, statement, visitor_info
from ..write.walltext import wall_text
from .artist import PROFILES, make_artist
from .work import make_work, pick_archetype

DAYS = {"May": 9, "September": 20, "December": 12, "June": 7, "October": 4, "November": 22, "January": 11, "March": 31}


def _person(rng, taken: set[str]) -> str:
    w = corpus.world()
    for _ in range(40):
        region = weighted(rng, w["regions"])
        name = f"{pick(rng, region['first'])} {pick(rng, region['last'])}"
        if name not in taken and name.lower() not in corpus.real_names():
            taken.add(name)
            return name
    raise RuntimeError("no name")


def generate(seed: int, n_works: int = 16, host_id: str | None = None, year: int | None = None) -> Exhibition:
    w = corpus.world()
    lx = corpus.lexicon()
    rng = sub_rng(seed, "exhibition")
    host = next(h for h in w["hosts"] if h["id"] == host_id) if host_id else weighted(rng, w["hosts"])
    year = year or rng.choice([2026, 2027, 2027])
    edition = rng.randint(3, 19)
    edition_name = f"{ordinal(edition)} {pick(rng, host['edition_names'])}"
    institution = pick(rng, host["institutions"])
    metaphor = pick(rng, lx["metaphors"])
    title = pick(rng, metaphor["titles"])
    taken: set[str] = set()
    poet = _person(rng, taken)
    poet_region = weighted(rng, w["regions"])
    title_source = fill(pick(rng, lx["title_sources"]), {
        "poet": poet, "poet_city": pick(rng, poet_region["born"]), "image": metaphor["image"], "city": host["city"],
        "poss_grandmother": pick(rng, ["her grandmother", "his grandmother", "their grandmother"])})
    open_m, close_m = host["season"]
    opening = f"{DAYS.get(open_m, 10)} {open_m} {year}"
    closing = f"{DAYS.get(close_m, 20)} {close_m} {year if close_m not in ('January', 'March') else year + 1}"

    director = _person(rng, taken)
    co = [_person(rng, taken) for _ in range(rng.randint(2, 4))]
    team = [Person(director, "Artistic Director", fill(pick(rng, lx["curator_bios"]), {"city": pick(rng, weighted(rng, w["regions"])["lives"])}))]
    team += [Person(n, pick(rng, ["Curator", "Associate Curator", "Curatorial Advisor"]),
                    fill(pick(rng, lx["curator_bios"]), {"city": pick(rng, weighted(rng, w["regions"])["lives"])})) for n in co]

    n_venues = min(len(host["venues"]), rng.randint(4, 6))
    venues = [Venue(**v) for v in pick(rng, host["venues"], n_venues)]
    if not any("video" in v.families for v in venues):
        extra = next((v for v in host["venues"] if "video" in v["families"]), None)
        if extra:
            venues.append(Venue(**extra))
    n_sections = rng.randint(3, 5)
    section_titles = pick(rng, metaphor["sections"], n_sections)
    sections = [Section(id=slugify(t, 30), title=t, text=x)
                for t, x in zip(section_titles, section_texts(sub_rng(seed, "sections"), section_titles, metaphor))]

    ex = Exhibition(seed=seed, slug=f"{seed}-{slugify(title, 40)}", institution=institution, edition=edition,
                    edition_name=edition_name, title=title, title_source=title_source, city=host["city"],
                    country=host["country"], year=year, opening=opening, closing=closing, team=team,
                    sections=sections, venues=venues, artists=[], works=[], identity=pick(rng, w["identities"]),
                    generator=f"artgen {__version__}")

    # line-up: guarantee a historical section and at least one collective, as real line-ups do
    profiles = [weighted(rng, PROFILES)["id"] for _ in range(n_works)]
    if "rediscovered" not in profiles:
        profiles[0] = "rediscovered"
    if "collective" not in profiles and n_works > 6:
        profiles[1] = "collective"
    used_archetypes: set[str] = set()
    used_titles: set[str] = set()
    names: set[str] = set(taken)
    for i, profile in enumerate(profiles):
        arng = sub_rng(seed, "artist", i)
        artist = make_artist(arng, i + 1, year, names, profile=profile)
        names.add(artist.name)
        wrng = sub_rng(seed, "work", i)
        arch = pick_archetype(wrng, artist, avoid=used_archetypes)
        used_archetypes.add(arch["id"])
        fitting = [v for v in venues if arch["family"] in v.families]
        if not fitting:  # open another venue rather than hang a painting in a boatyard
            spare = [Venue(**v) for v in host["venues"] if arch["family"] in v["families"] and v["id"] not in {x.id for x in venues}]
            if spare:
                venues.append(spare[0])
                fitting = [spare[0]]
        venue = pick(wrng, fitting or venues)
        section = sections[i % len(sections)]
        work = make_work(wrng, i + 1, artist, venue, section.id, year, edition_name, arch=arch, used_titles=used_titles)
        trng = sub_rng(seed, "text", i)
        work.wall_text = tidy(wall_text(trng, artist, work, edition_name))
        author_name = pick(trng, [p.name for p in team] + [_person(trng, names)])
        author_role = fill(pick(trng, lx["essay"]["author_roles"]), {"city": city(pick(trng, artist.lives or [artist.born_place or "Venice"])), "edition": edition_name})
        work.essay, work.references, _ = essay(trng, artist, work, venue, edition_name, author_name)
        work.essay = tidy(work.essay)
        work.essay_author = f"{author_name}, {author_role}"
        artist.bio = tidy(bio(trng, artist, work, year))
        work.prompt = image_prompt(sub_rng(seed, "prompt", i), work, venue)
        ex.artists.append(artist)
        ex.works.append(work)

    order = {s.id: k for k, s in enumerate(sections)}
    ex.works.sort(key=lambda x: (order[x.section_id], x.venue_id, x.id))
    srng = sub_rng(seed, "statement")
    ex.statement = statement(srng, ex, metaphor, director, co)
    ex.press_release = press_release(srng, ex, director, co)
    ex.visitor_info = visitor_info(ex)
    return ex
