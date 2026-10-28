import numpy as np


def value_range(values):
    """Return the range (maximum minus minimum) of the values."""
    return np.ptp(np.asarray(values))
