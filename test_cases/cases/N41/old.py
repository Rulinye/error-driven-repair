import numpy as np


def joint_density(x, y, bins):
    """Return the 2-D histogram of x and y, normalised so that its integral is 1, and the bin edges."""
    return np.histogram2d(x, y, bins=bins, normed=True)
