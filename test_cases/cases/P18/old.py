def time_into_month(stamps):
    """Return, for each timestamp, the time elapsed since the start of its month."""
    return stamps.to_perioddelta("M")
