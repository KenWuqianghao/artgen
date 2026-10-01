"""Small, stateless text and randomness helpers shared by every generator."""
from __future__ import annotations

import hashlib
import random
import re
import unicodedata

SMALL_WORDS = {"a", "an", "and", "as", "at", "but", "by", "for", "from", "in", "into",
               "nor", "of", "on", "or", "the", "to", "with", "without"}


def sub_rng(seed: int | str, *parts) -> random.Random:
    """A deterministic RNG for one entity. Same seed and parts give the same stream,
    so adding a new generator never shifts the randomness of another one."""
    key = "/".join(str(p) for p in (seed, *parts))
    digest = hashlib.sha256(key.encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def weighted(rng: random.Random, items: list[dict], key: str = "weight"):
    return rng.choices(items, weights=[i.get(key, 1) for i in items], k=1)[0]


def pick(rng: random.Random, items, k: int | None = None):
    items = list(items)
    if k is None:
        return rng.choice(items)
    return rng.sample(items, min(k, len(items)))


def a_an(word: str) -> str:
    w = word.strip().lower()
    if not w:
        return "a"
    if re.match(r"^(eu|uni|use|one|u[bcfhjkqrst][aeiou])", w):
        return "a"
    if re.match(r"^(hour|honou?r|heir)", w) or w[0] in "aeiou":
        return "an"
    return "a"


def with_article(phrase: str) -> str:
    return f"{a_an(phrase)} {phrase}"


def fix_articles(text: str) -> str:
    def repl(m):
        art, word = m.group(1), m.group(2)
        right = a_an(word)
        if art[0].isupper():
            right = right.capitalize()
        return f"{right} {word}"
    return re.sub(r"\b([Aa]n?) ([A-Za-z][\w'-]*)", repl, text)


def join_list(items, conj: str = "and", oxford: bool = False) -> str:
    items = [i for i in items if i]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} {conj} {items[1]}"
    comma = "," if oxford else ""
    return ", ".join(items[:-1]) + f"{comma} {conj} " + items[-1]


def title_case(s: str) -> str:
    words = s.split()
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        if 0 < i < len(words) - 1 and lw in SMALL_WORDS:
            out.append(lw)
        elif w[:1].islower():
            out.append(w[:1].upper() + w[1:])
        else:
            out.append(w)
    return " ".join(out)


def cap(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s


def slugify(s: str, maxlen: int = 60) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^\w\s-]", "", s.lower())
    return re.sub(r"[\s_-]+", "-", s).strip("-")[:maxlen].strip("-") or "untitled"


def ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suf = "th"
    else:
        suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


def fill(template: str, slots: dict) -> str:  # noqa: D401
    """Replace {name} slots. Unknown slots are left visible so missing data is easy to spot."""
    def repl(m):
        k = m.group(1)
        return str(slots[k]) if k in slots else m.group(0)
    return re.sub(r"\{([A-Za-z_0-9]+)\}", repl, template)


def plural(noun: str) -> str:
    last = noun.split()[-1]
    if last.endswith(("ss", "x", "ch", "sh")):
        return noun + "es"
    if last.endswith("s"):
        return noun
    if last.endswith("y") and len(last) > 1 and last[-2] not in "aeiou":
        return noun[:-1] + "ies"
    return noun + "s"


NUMBER_WORDS = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
                10: "ten", 11: "eleven", 12: "twelve", 20: "twenty", 40: "forty", 100: "a hundred"}


def number_word(n: int) -> str:
    return NUMBER_WORDS.get(n, str(n))


def sentence_case(text: str) -> str:
    """Capitalise the first letter of every sentence, leaving the rest untouched."""
    return re.sub(r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text)


_SMALL = {"2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine"}


def spell_small_numbers(text: str) -> str:
    """House style for prose: one-digit counts as words, but keep '4-channel', '6 min.', '3 × 4 cm' and decimals."""
    def repl(m):
        word = _SMALL[m.group(1)]
        start = m.start()
        sentence_start = start == 0 or text[max(0, start - 2):start] in (". ", "? ", "! ")
        return word.capitalize() if sentence_start else word
    return re.sub(r"(?<![\d.,×–-])\b([2-9])\b(?![\d.,×–]| ×|-channel| ?(?:cm|min|sec|hrs|tonnes|kg)\b|%)", repl, text)


def tidy(text: str) -> str:
    """Collapse doubled spaces and full stops ('D.C..'), keep paragraph breaks and ellipses."""
    text = re.sub(r"(?<!\.)\.\.(?!\.)", ".", text)
    return re.sub(r"[ \t]{2,}", " ", text)
