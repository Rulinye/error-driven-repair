import numpy as np


def columns_with_negatives(table):
    """Return the indices of the columns of the 2-D table that contain at least one negative value."""
    t = np.asarray(table)
    return np.flatnonzero(np.any(t < 0, axis=0)).tolist()
