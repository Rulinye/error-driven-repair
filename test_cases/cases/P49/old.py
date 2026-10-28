import pandas as pd


def to_dates(day_texts):
    """Return the date strings (YYYY-MM-DD) as a Series of dates."""
    return pd.Series(day_texts, dtype="datetime64[D]")
