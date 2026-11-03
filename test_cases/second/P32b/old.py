import io

import pandas as pd


def read_sensor_log(text):
    """Read a semicolon-separated sensor log, leaving out the lines with more fields than the header."""
    return pd.read_csv(io.StringIO(text), sep=";", error_bad_lines=False)
