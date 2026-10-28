def week_numbers(stamps):
    """Return the week of the year of each timestamp of a DatetimeArray, as a list of ints."""
    return [int(w) for w in stamps.dayofyear]
