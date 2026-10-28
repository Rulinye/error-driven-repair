import io

import pandas as pd


def read_skipping_bad_lines(text):
    """Read CSV text, skipping the lines that have more fields than the header."""
    return pd.read_csv(io.StringIO(text), on_bad_lines="skip")
