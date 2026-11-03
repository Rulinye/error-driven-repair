"""quillery: helpers for cleaning, splitting and laying out plain text."""

import re
import unicodedata

__version__ = "3.2.1"

_WORD = re.compile(r"\w+(?:['’]\w+)*")
_SMALL = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "of", "on", "or", "the", "to"}


def _accents_off(text):
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def normalize(text, strip_accents=False, lower=False):
    """Collapse runs of whitespace to single spaces; optionally remove accents and lower the case."""
    out = " ".join(str(text).split())
    if strip_accents:
        out = _accents_off(out)
    if lower:
        out = out.lower()
    return out


def slugify(text, sep="-"):
    """A lowercase ASCII identifier made of the words of the text, joined by sep."""
    words = re.findall(r"[a-z0-9]+", _accents_off(str(text)).lower())
    return sep.join(words)


def wrap(text, width=40):
    """The words of the text laid out greedily in lines of at most width characters."""
    lines, line = [], ""
    for word in str(text).split():
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}" if line else word
    if line:
        lines.append(line)
    return lines


def word_count(text):
    """The number of words in the text."""
    return len(_WORD.findall(str(text)))


def char_count(text, spaces=True):
    """The number of characters, with or without whitespace."""
    text = str(text)
    return len(text) if spaces else sum(1 for ch in text if not ch.isspace())


def title_case(text):
    """Capitalize every word."""
    return " ".join(w[:1].upper() + w[1:] for w in str(text).split())


def truncate(text, limit, ellipsis="…"):
    """At most limit characters of the text, followed by the ellipsis if anything was cut."""
    text = str(text)
    return text if len(text) <= limit else text[:limit] + ellipsis


class Tokenizer:
    """Splits text into words or sentences."""

    def __init__(self, keep_punct=False):
        self.keep_punct = keep_punct

    def words(self, text):
        """The words of the text, with punctuation marks as separate tokens if keep_punct is set."""
        pattern = r"\w+(?:['’]\w+)*|[^\w\s]" if self.keep_punct else _WORD.pattern
        return re.findall(pattern, str(text))

    def sentences(self, text):
        """The sentences of the text, split after '.', '!' or '?'."""
        parts = re.split(r"(?<=[.!?])\s+", str(text).strip())
        return [p for p in parts if p]
