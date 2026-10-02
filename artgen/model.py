"""The data model. exhibition.json is the contract between generate, render and site."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Artist:
    id: str
    name: str
    sort_name: str
    collective: bool
    pronoun: str                      # she / he / they
    born_year: int | None
    born_place: str | None
    died_year: int | None
    lives: list[str]                  # cities, empty for the deceased
    profile: str                      # archetype of career, e.g. "heritage", "rediscovered"
    heritage: str                     # the practice or history the work draws on
    origin: str = ""                  # id of the origin pool in world.json
    members: list[str] = field(default_factory=list)
    founded_year: int | None = None
    bio: str = ""

    @property
    def life_line(self) -> str:
        """Label line in the Venice 2026 style: 'Born 1983, Manila, Philippines. Lives in London, UK'."""
        if self.collective:
            return f"Founded {self.founded_year}, {self.born_place}"
        if self.died_year:
            return f"Born {self.born_year}, {self.born_place}. D. {self.died_year}"
        if len(self.lives) == 1:
            return f"Born {self.born_year}, {self.born_place}. Lives in {self.lives[0]}"
        return f"Born {self.born_year}, {self.born_place}. Lives in {self.lives[0]}, and {self.lives[1]}"


def city(place: str) -> str:
    """'Manila, Philippines' -> 'Manila'; 'Washington, D.C., USA' -> 'Washington, D.C.'."""
    return place.rsplit(", ", 1)[0] if place and ", " in place else place


@dataclass
class Venue:
    id: str
    name: str
    description: str                  # for prompts: what the room looks like
    floor: str
    light: str
    families: list[str] = field(default_factory=list)
    room: str = ""                    # industrial / white / historic / dark / outdoor: what a photo of it looks like


@dataclass
class Work:
    id: str
    slug: str
    artist_id: str
    title: str
    year: int | str
    archetype: str
    family: str
    kind: str                         # installation, painting, video, sound, performance
    form: str                         # human label, e.g. "Textile installation"
    medium: str                       # the medium line on the tombstone label
    dimensions: str
    scene: str                        # what a visitor sees, one or two sentences
    materials: list[str]
    nonvisual: list[str]
    themes: list[str]
    references: list[str]             # theorists and writers the texts lean on
    claims: list[str]
    venue_id: str
    section_id: str
    courtesy: str
    support: str
    photo_credit: str
    wall_text: str = ""
    essay: str = ""
    essay_author: str = ""
    prompt: str = ""
    media: str | None = None          # path relative to the exhibition dir
    media_kind: str | None = None     # image / placeholder
    extra: dict = field(default_factory=dict)   # generation details: fact, process, quote, camera, basis


@dataclass
class Section:
    id: str
    title: str
    text: str


@dataclass
class Person:
    name: str
    role: str
    bio: str = ""


@dataclass
class Exhibition:
    seed: int
    slug: str
    institution: str                  # the fictional organiser
    edition: int
    edition_name: str                 # e.g. "16th Salt Coast Biennial"
    title: str
    title_source: str                 # where the title comes from
    city: str
    country: str
    year: int
    opening: str
    closing: str
    team: list[Person]
    sections: list[Section]
    venues: list[Venue]
    artists: list[Artist]
    works: list[Work]
    statement: list[str] = field(default_factory=list)
    press_release: list[str] = field(default_factory=list)
    visitor_info: list[str] = field(default_factory=list)
    identity: dict = field(default_factory=dict)
    generator: str = ""
    options: dict = field(default_factory=dict)

    # ---- lookups
    def artist(self, artist_id: str) -> Artist:
        return next(a for a in self.artists if a.id == artist_id)

    def venue(self, venue_id: str) -> Venue:
        return next(v for v in self.venues if v.id == venue_id)

    def section(self, section_id: str) -> Section:
        return next(s for s in self.sections if s.id == section_id)

    def works_in(self, section_id: str) -> list[Work]:
        return [w for w in self.works if w.section_id == section_id]

    # ---- persistence
    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, directory: Path) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "exhibition.json"
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return path

    @classmethod
    def load(cls, directory: Path) -> "Exhibition":
        d = json.loads((directory / "exhibition.json").read_text(encoding="utf-8"))
        return cls(
            **{k: v for k, v in d.items() if k not in {"team", "sections", "venues", "artists", "works"}},
            team=[Person(**p) for p in d["team"]],
            sections=[Section(**s) for s in d["sections"]],
            venues=[Venue(**v) for v in d["venues"]],
            artists=[Artist(**a) for a in d["artists"]],
            works=[Work(**w) for w in d["works"]],
        )
