import numpy as np


def names_array(names):
    """Return the names as a NumPy array of Unicode text."""
    return np.array(names, dtype=np.bytes_)
