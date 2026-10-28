import numpy as np


def scalar_type_of(spec):
    """Return the NumPy scalar type for a dtype given as a string, a type or a dtype."""
    return np.obj2sctype(spec)
