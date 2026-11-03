import quillery


def search_key(name):
    """Return the form of a name used for searching: single spaces, no accents, lower case."""
    return quillery.normalize(name, lower=True)
