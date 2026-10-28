def all_readings(morning, evening):
    """Return the morning readings followed by the evening readings, labelled from 0."""
    return morning.append(evening, ignore_index=True)
