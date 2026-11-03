def names_above(scores, limit):
    """Return the labels of the scores above the limit, in their order."""
    return scores.index[scores > limit].tolist()
