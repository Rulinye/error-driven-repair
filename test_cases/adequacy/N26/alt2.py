import numpy as np


def precise_sum(values):
    """Sum the values in extended precision."""
    return np.asarray(values, dtype=np.longdouble).sum()
