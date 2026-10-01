"""Image prompts in the style of real installation documentation (see docs/research/part_photo.json):
empty or nearly empty rooms, neutral light, straight verticals, horizontal frame, no visible text."""
from __future__ import annotations

import random

from .model import Venue, Work
from .textkit import join_list

TEXT_FAMILIES_ALLOWED = {"text-painting", "neon-slogan"}


def image_prompt(rng: random.Random, w: Work, v: Venue) -> str:
    people = rng.random() < w.extra.get("people_p", 0.2) * 0.6
    who = ("One or two visitors in ordinary clothes stand at a distance, seen from behind, small in the frame."
           if people else "No people in the room.")
    if w.archetype in TEXT_FAMILIES_ALLOWED:
        text_rule = "The only legible text is the artwork's own phrase, spelled exactly as given."
    else:
        text_rule = "No legible text anywhere; any wall label is small, blank and out of focus."
    video = w.kind == "video"
    room = v.description if not video else f"{v.description} The room is darkened for moving image; the projector and a bench are visible."
    return (
        "Installation view photograph from the press kit of an international contemporary art biennial. "
        f"Room: {room} Floor: {v.floor}. Light: {v.light}. "
        f"The artwork: {w.scene} Materials: {join_list(w.materials)}. "
        f"Framing: {w.extra.get('camera', 'wide view at eye level')}; horizontal 3:2 frame, camera at chest height, straight verticals, "
        "a slice of the neighbouring room or doorway visible at one edge. "
        f"{who} "
        "Style: professional exhibition documentation, neutral white balance, even natural exposure, slightly muted colours, high detail, "
        "the kind of image published on Contemporary Art Daily or a museum press page. Unremarkable and credible. "
        f"Not cinematic: no dramatic spotlight, no lens flare, no haze unless the artwork makes it, no vignette. {text_rule} No watermark."
    )
