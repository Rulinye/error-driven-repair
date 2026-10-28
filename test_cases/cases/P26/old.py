def spread(values):
    """Return the mean absolute deviation of the values around their mean, ignoring missing values."""
    return values.mad()
