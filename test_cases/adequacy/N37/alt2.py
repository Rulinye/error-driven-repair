import numpy as np


def safe_sum(arr, axis):
    """Sum the array along the axis; return None if the array has no such axis."""
    ndim = np.ndim(arr)
    axes = () if axis is None else axis if isinstance(axis, tuple) else (axis,)
    if any(not -ndim <= a < ndim for a in axes):
        return None
    return np.sum(arr, axis=axis)
