def hourly_means(readings):
    """Average the readings per hour; each hour is labelled by its end instead of its start."""
    return readings.resample("1H", loffset="1H").mean()
