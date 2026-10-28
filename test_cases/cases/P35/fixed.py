import pandas as pd


def hourly_means(readings):
    """Average the readings per hour; each hour is labelled by its end instead of its start."""
    out = readings.resample("1H").mean()
    out.index = out.index + pd.Timedelta("1H")
    return out
