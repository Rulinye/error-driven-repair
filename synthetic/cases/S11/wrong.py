import quillery


def article_url(title, article_id):
    """Return the URL path of an article: its id followed by a lowercase ASCII form of the title."""
    return f"/articles/{article_id}-{quillery.normalize(title, lower=True).replace(' ', '-')}"
