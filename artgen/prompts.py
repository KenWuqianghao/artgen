"""Build prompts for image and video generation models from an artwork spec."""
import re


def _and_list(items):
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def _kw(k):
    return re.sub(r"^the ", "", k)


def image_prompt(spec):
    """Prompt for exhibition documentation of the work."""
    if spec["kind"] == "video":
        subject = (
            (f"a dark gallery with one very large floor-to-ceiling video projection; " if spec["channels"] == 1 else
             f"a dark gallery with {spec['channels']} large video screens of different sizes at different heights; ") +
            f"on the screens: {spec['video_motifs'][0]}, {spec['video_motifs'][1]}, {spec['video_motifs'][2]}; "
            f"screens glow and light the concrete floor; a few silhouetted visitors sit on the floor"
        )
    else:
        subject = (
            f"a large-scale contemporary art installation made of {_and_list(spec['materials'])}, {spec['technique']}"
        )
    return (
        f"{subject}. Located in {spec['venue']}, Venice Biennale. "
        f"The work evokes {spec['theme']} and {_kw(spec['keyword'])}. "
        f"{spec['photo_style']}. No text, no captions, no watermark."
    )


def video_prompt(spec):
    """Prompt for a short video model clip: either the artwork itself or a walk-through."""
    if spec["kind"] == "video":
        motif = spec["video_motifs"][0]
        return (
            f"{motif}. {spec['video_style']}. A contemporary art video about {spec['theme']} and {_kw(spec['keyword'])}. "
            f"Minimal, contemplative, no dialogue, no text on screen."
        )
    return (
        f"Slow walk-through of a contemporary art installation made of {_and_list(spec['materials'])}, {spec['technique']}, "
        f"inside {spec['venue']}. {spec['video_style']}. No people speak. No text on screen."
    )


def negative_prompt():
    return "text, watermark, logo, caption, cartoon, anime, illustration, blurry, low quality, oversaturated"
