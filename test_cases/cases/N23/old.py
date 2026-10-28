import numpy as np


def is_integer_array(arr):
    """Return True if the array holds integers of any size, signed or unsigned."""
    return np.issubsctype(arr, np.integer)
