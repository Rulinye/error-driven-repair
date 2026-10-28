import io

import pandas as pd


def read_column(text):
    """Read CSV text that has a single column and return that column as a Series."""
    return pd.read_csv(io.StringIO(text)).squeeze("columns")
