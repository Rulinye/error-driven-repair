import io

import pandas as pd


def read_headerless(text):
    """Read CSV text that has no header row; the columns are named col0, col1, ..."""
    return pd.read_csv(io.StringIO(text), header=None).add_prefix("col")
