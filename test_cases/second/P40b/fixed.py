def cap_values(values, limit):
    """Return the values with every value above the limit replaced by the limit."""
    return values.where(values <= limit, limit)
