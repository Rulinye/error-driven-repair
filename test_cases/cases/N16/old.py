import numpy as np


def all_positive(values):
    """Return True if every value is positive."""
    return bool(np.alltrue(np.asarray(values) > 0))
