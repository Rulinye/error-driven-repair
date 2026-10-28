def running_max(values):
    """Return the running maximum of the values."""
    return values.expanding().max()
