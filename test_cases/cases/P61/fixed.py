def pick(labels, positions):
    """Return the labels (a Categorical) at the given positions, in that order."""
    return labels.take(positions)
