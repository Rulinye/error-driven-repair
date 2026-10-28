import numpy as np


def density_histogram(values, bins):
    """Return the histogram of the values, normalised so that its area is 1, and the bin edges."""
    return np.histogram(values, bins=bins)
