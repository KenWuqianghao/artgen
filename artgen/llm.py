"""Optional: expand the templated essay into a longer, more fluent one with Claude.

Needs the `anthropic` package and credentials (ANTHROPIC_API_KEY or `ant auth login`).
"""

SYSTEM = """You are a senior curatorial writer for a major international biennale.
You write in flawless International Art English: nominalised abstractions, paired near-synonyms,
adverb-verb pairs ("quietly interrogates"), theory citations used as ornament, and a principled refusal
to conclude. You take the work completely seriously. You never wink at the reader. You never explain the joke,
because for you there is no joke."""


def expand_essay(spec, draft_essay, words=1200, model="claude-opus-5"):
    try:
        import anthropic
    except ImportError as e:
        raise RuntimeError("pip install anthropic  (the --llm flag needs it)") from e

    client = anthropic.Anthropic()
    prompt = (
        f"Below is a draft curatorial essay about a new commission for the Venice Biennale, plus the artwork's facts.\n"
        f"Rewrite and expand it into a polished essay of about {words} words for the exhibition catalogue.\n"
        f"Keep every fact (title, artist, materials, venue, theorists, footnotes). Add two or three more footnotes in the same style. "
        f"Keep the epigraph. Keep the byline at the end. Output Markdown only.\n\n"
        f"## Facts\n"
        f"Title: {spec['title']}\nArtist: {spec['artist']}\nYear: {spec['year']}\nForm: {spec['form']}\n"
        f"Materials: {', '.join(spec['materials'])}\nTechnique: {spec['technique']}\nVenue: {spec['venue']}\n"
        f"Theme: {spec['theme']} / {spec['theme_secondary']}\n\n"
        f"## Draft\n{draft_essay}"
    )
    with client.beta.messages.stream(
        model=model,
        max_tokens=16000,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        thinking={"type": "adaptive"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    ) as stream:
        msg = stream.get_final_message()
    if msg.stop_reason == "refusal":
        raise RuntimeError(f"model refused: {getattr(msg, 'stop_details', None)}")
    return "".join(b.text for b in msg.content if b.type == "text")
