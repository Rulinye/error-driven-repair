import pandas as pd


def all_readings(morning, evening):
    """Return the morning readings followed by the evening readings, labelled from 0."""
    return pd.concat([morning, evening], ignore_index=True)
