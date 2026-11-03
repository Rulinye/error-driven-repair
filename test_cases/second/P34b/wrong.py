def quarter_hour_counts(events):
    """Count the events in 15-minute bins that start 5 minutes past the quarter hour (00:05, 00:20, ...)."""
    return events.resample("15min", offset=5).count()
