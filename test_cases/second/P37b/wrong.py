import pandas as pd


def billing_months(first, last):
    """Return the first day of every month from first up to, but not including, last."""
    return pd.date_range(first, last, freq="MS")
