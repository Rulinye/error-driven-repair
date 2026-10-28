def in_time_order(log):
    """Return True if the index of the log never decreases."""
    return log.index.is_monotonic
