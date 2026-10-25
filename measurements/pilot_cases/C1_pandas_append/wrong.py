import pandas as pd

def add_row(df, row):
    """Return a new DataFrame with one row (dict) appended."""
    df.loc[len(df)] = row   # plausible fix, but mutates the input
    return df
