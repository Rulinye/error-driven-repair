def stamps_as_series(stamps):
    """Return the timestamps as a Series whose index is the timestamps, keeping their time zone."""
    return stamps.to_series(keep_tz=True)
