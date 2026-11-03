import numpy as np
from numpy.exceptions import AxisError


def safe_sum(arr, axis):
    """Sum the array along the axis; return None if the array has no such axis."""
    try:
        return np.sum(arr, axis=axis)
    except AxisError:
        return None
