import numpy as np


def is_integer_array(arr):
    """Return True if the array holds integers of any size, signed or unsigned."""
    return arr.dtype == np.int64
