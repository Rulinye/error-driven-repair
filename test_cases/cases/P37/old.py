import pandas as pd


def days_between(start, end):
    """Return every day from start up to, but not including, end."""
    return pd.date_range(start, end, freq="D", closed="left")
