def time_into_month(stamps):
    """Return, for each timestamp, the time elapsed since the start of its month."""
    return stamps - stamps.to_period("M").to_timestamp()
