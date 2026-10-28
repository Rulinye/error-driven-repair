def morning_rows(log):
    """Return the rows logged from 08:00 up to, but not including, 12:00."""
    return log.between_time("08:00", "12:00")
