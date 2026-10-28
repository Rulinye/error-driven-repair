import numpy as np


def cumulative_growth(rates):
    """Return the growth factor after each step of a sequence of growth rates (0.1 means +10%)."""
    return np.prod(1 + np.asarray(rates))
