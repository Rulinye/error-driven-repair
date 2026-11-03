import io

import pandas as pd


def read_ids(text):
    """Read the "id" column of CSV text and return it as a Series."""
    return pd.read_csv(io.StringIO(text), usecols=["id"], squeeze=True)
