"""quillery: helpers for cleaning, splitting and laying out plain text."""

import re
import textwrap
import unicodedata

__version__ = "4.0.0"

_WORD = re.compile(r"\w+(?:['’]\w+)*")
_SMALL = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "of", "on", "or", "the", "to"}


def _accents_off(text):
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def normalize(text, fold=None, lower=False):
    """Collapse runs of whitespace to single spaces. fold="ascii" removes accents; lower lowers the case."""
    if fold not in (None, "ascii"):
        raise ValueError("fold must be None or 'ascii'")
    out = " ".join(str(text).split())
    if fold == "ascii":
        out = _accents_off(out)
    if lower:
        out = out.lower()
    return out


def to_handle(text, sep="-"):
    """A lowercase ASCII identifier made of the words of the text, joined by sep."""
    words = re.findall(r"[a-z0-9]+", _accents_off(str(text)).lower())
    return sep.join(words)


def wrap(text, measure=40):
    """The words of the text laid out greedily in lines of at most measure characters."""
    lines, line = [], ""
    for word in str(text).split():
        if line and len(line) + 1 + len(word) > measure:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}" if line else word
    if line:
        lines.append(line)
    return lines


class TextDigest:
    """Counts of a text: words, characters and lines."""

    def __init__(self, text):
        text = str(text)
        self.words = len(_WORD.findall(text))
        self.chars = len(text)
        self.lines = len(text.splitlines()) if text else 0

    def __repr__(self):
        return f"TextDigest(words={self.words}, chars={self.chars}, lines={self.lines})"


def digest(text):
    """The counts of a text (TextDigest)."""
    return TextDigest(text)


def char_count(text, spaces=True):
    """The number of characters, with or without whitespace."""
    text = str(text)
    return len(text) if spaces else sum(1 for ch in text if not ch.isspace())


def title_case(text):
    """Capitalize every word except short function words that are not the first word."""
    words = str(text).split()
    return " ".join(w if i and w.lower() in _SMALL else w[:1].upper() + w[1:] for i, w in enumerate(words))


def truncate(text, limit, ellipsis="…"):
    """At most limit characters, the ellipsis included, if anything was cut."""
    text = str(text)
    return text if len(text) <= limit else text[:max(limit - len(ellipsis), 0)] + ellipsis


def dedent_block(text):
    """The text with the common leading whitespace of its lines removed."""
    return textwrap.dedent(str(text)).strip("\n")


class Tokenizer:
    """Splits text into words or sentences."""

    def __init__(self, keep_punct=False):
        self.keep_punct = keep_punct

    def scan(self, text):
        """The words of the text, with punctuation marks as separate tokens if keep_punct is set."""
        pattern = r"\w+(?:['’]\w+)*|[^\w\s]" if self.keep_punct else _WORD.pattern
        return re.findall(pattern, str(text))

    def sentences(self, text):
        """The sentences of the text, split after '.', '!' or '?'."""
        parts = re.split(r"(?<=[.!?])\s+", str(text).strip())
        return [p for p in parts if p]
