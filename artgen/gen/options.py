"""Curator options: everything a person can choose in the Studio or on the command line."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

MIX = {"none": 0, "some": 1, "many": 3}   # multiplier on the default share of a profile in the line-up


@dataclass
class Options:
    seed: int
    works: int = 16
    host: str | None = None            # world.json host id; None = chosen by seed
    theme: str | None = None           # lexicon metaphor id; None = chosen by seed
    title: str | None = None           # custom edition title
    forms: list[str] = field(default_factory=list)   # allowed archetype families; empty = all
    rediscovered: str = "some"         # none / some / many
    collectives: str = "some"
    emerging: str = "some"
    jargon: int = 2                    # 1 plain, 2 usual, 3 unbearable
    identity: str | None = None        # world.json identity name; None = chosen by seed
    year: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)
