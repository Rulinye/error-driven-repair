def two_hour_totals(readings):
    """Sum hourly readings in 2-hour bins that start at odd hours (23:00, 01:00, 03:00, ...)."""
    return readings.resample("2H", base=1).sum()
