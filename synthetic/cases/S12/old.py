import quillery


def longest_word(text):
    """Return the longest word of the text; the first one if several have the same length."""
    words = quillery.Tokenizer().words(text)
    return max(words, key=len) if words else ""
