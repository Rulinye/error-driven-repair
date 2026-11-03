import numpy as np


def nearest_position(index, value):
    """Return the position of the label nearest to the value in a sorted numeric index."""
    distances = np.abs(index.to_numpy() - value)
    return int(np.flatnonzero(distances == distances.min())[-1])
