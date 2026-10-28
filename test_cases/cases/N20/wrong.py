import numpy as np


def to_dtype(values, dtype):
    """Return the values converted to the given dtype."""
    return np.asarray(values).view(dtype)
