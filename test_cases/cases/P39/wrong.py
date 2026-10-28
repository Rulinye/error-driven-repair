import pandas as pd


def encode(values):
    """Return integer codes for the values (missing values get -1) and the distinct values."""
    codes, uniques = pd.factorize(values, use_na_sentinel=False)
    return codes, uniques
