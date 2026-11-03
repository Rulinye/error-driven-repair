import numpy as np


def missing_block(rows, cols):
    """Return a rows x cols array of missing values (NaN)."""
    return np.full((rows, cols), np.nan)
