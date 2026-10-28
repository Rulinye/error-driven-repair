import numpy as np


def type_code(scalar_type):
    """Return the one-character code of a scalar type, such as 'd' for float64."""
    return np.dtype(scalar_type).char
