import pandas as pd


def stamps_as_series(stamps):
    """Return the timestamps as a Series whose index is the timestamps, keeping their time zone."""
    return pd.Series(stamps, index=stamps, name=stamps.name)
