def date_summary(events):
    """Return count, mean, minimum, quartiles and maximum of the date column."""
    return events["date"].describe(datetime_is_numeric=True)
