import numpy as np


def is_float_type(t):
    """Return True if the given type is a NumPy floating-point scalar type."""
    return np.issubclass_(t, np.floating)
