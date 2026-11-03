import quillery


def reading_minutes(text, words_per_minute=200):
    """Return the estimated reading time of the text in whole minutes, at least one."""
    return max(1, round(quillery.word_count(text) / words_per_minute))
