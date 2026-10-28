import numpy as np


def growth_factor(rates):
    """Return the total growth factor of a sequence of growth rates (0.1 means +10%)."""
    return np.cumprod(1 + np.asarray(rates))
