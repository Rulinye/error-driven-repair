import numpy as np


def any_missing(values):
    """Return True if at least one value is NaN."""
    return bool(np.asmatrix(np.isnan(values)))
