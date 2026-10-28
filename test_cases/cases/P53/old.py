import pandas as pd


def readings_series(values):
    """Return the sensor readings as a Series."""
    return pd.Series(values, dtype="int64")
