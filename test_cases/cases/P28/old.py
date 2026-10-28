def one_day_later(daily):
    """Return the daily Series with every date moved one day later; the values stay as they are."""
    return daily.tshift(1)
