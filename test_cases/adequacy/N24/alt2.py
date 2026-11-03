import numpy as np


def is_float_type(t):
    """Return True if the given type is a NumPy floating-point scalar type."""
    try:
        return issubclass(t, np.floating)
    except TypeError:
        return False
