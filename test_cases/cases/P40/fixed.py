def clip_negatives(values):
    """Return the values with every negative value replaced by 0."""
    return values.where(values >= 0, 0)
