def busiest_week(stamps):
    """Return the week of the year that occurs most often among the timestamps of a DatetimeArray."""
    weeks = [int(w) for w in stamps.month]
    return max(sorted(set(weeks)), key=weeks.count)
