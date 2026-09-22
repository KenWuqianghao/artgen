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
    """Prompt for exhibition documentation of the work. Flat, honest, un-cinematic on purpose."""
    comp = spec.get("composition", "")
    if spec["kind"] == "video":
        if spec["channels"] and spec["channels"] > 1:
            subject = (f"a dark gallery with {spec['channels']} video projections of different sizes on temporary walls; "
                       f"on the screens: {comp}; some visitors' backs")
        else:
            subject = f"a dark room with one large video projection on a bare wall showing {comp}; a bench; the projector visible on a stand"
    elif spec["kind"] == "painting":
        subject = f"{comp}; {spec['materials'][0]}; hung on a wall"
    else:
        subject = f"{comp}; materials: {_and_list(spec['materials'])}"
    return (
        f"Documentation photograph of a contemporary artwork at the Venice Biennale, {spec['venue']}. "
        f"{subject}. "
        f"{spec['photo_style']}. Ordinary, slightly boring, credible. "
        f"No text overlays, no captions, no watermark, no dramatic lighting, no fog, no lens flare, no silhouettes against light."
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
        f"Slow handheld walk past a contemporary artwork: {spec.get('composition', '')}, inside {spec['venue']}. "
        f"{spec['video_style']}. No people speak. No text on screen."
    )


def negative_prompt():
    return "text, watermark, logo, caption, cartoon, anime, illustration, blurry, low quality, oversaturated"
