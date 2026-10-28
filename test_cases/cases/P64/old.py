def nearest_month(months, month):
    """Return the position of the period in the monthly PeriodIndex nearest to the given period."""
    return months.get_loc(month, method="nearest")
