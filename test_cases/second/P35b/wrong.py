def daily_totals_at_end(amounts):
    """Sum the amounts per day; each day is labelled by the midnight at its end."""
    return amounts.resample("1D", offset="1D").sum()
