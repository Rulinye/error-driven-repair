import numpy as np


def to_real_array(values):
    """Convert a list of numbers or numeric strings to an array of real numbers."""
    return np.array(values, dtype=np.float)
