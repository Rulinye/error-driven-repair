def in_range(values, low, high):
    """Return True where the value lies between low and high, both included."""
    return values.between(low, high, inclusive="both")
