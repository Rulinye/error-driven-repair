import pandas as pd

def add_row(df, row):
    """Return a new DataFrame with one row (dict) appended."""
    return df.append(row, ignore_index=True)
