def closest_quarter(quarters, when):
    """Return the position of the period in the quarterly PeriodIndex closest to the given period."""
    return quarters.get_loc(when, method="nearest")
