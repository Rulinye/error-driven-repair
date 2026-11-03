import pandas as pd


def encode(values):
    """Return integer codes for the values (missing values get -1) and the distinct values."""
    return pd.factorize(values, sort=False, use_na_sentinel=True)
