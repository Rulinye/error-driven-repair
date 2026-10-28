def names_above(scores, limit):
    """Return the labels of the scores above the limit, in their order."""
    return [name for name, value in scores.iteritems() if value > limit]
