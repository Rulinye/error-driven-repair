import numpy as np


def zero_of(spec):
    """Return the number zero as a NumPy scalar of the dtype given by spec (a string, a type or a dtype)."""
    return np.dtype(spec).type(0)
