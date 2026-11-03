import pandas as pd


def daily_totals_at_end(amounts):
    """Sum the amounts per day; each day is labelled by the midnight at its end."""
    out = amounts.resample("1D").sum()
    out.index = out.index + pd.Timedelta("1D")
    return out
