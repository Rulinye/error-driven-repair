import numpy as np


def mask_negative(values):
    """Return a copy of the values in which every negative value is replaced by NaN."""
    out = np.array(values, dtype=float)
    out[out < 0] = np.NaN
    return out
