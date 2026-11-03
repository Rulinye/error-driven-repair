import numpy as np


def rows_within(table, low, high):
    """Return, for each row of the 2-D table, whether all of its values lie in [low, high]."""
    t = np.asarray(table)
    return np.alltrue((t >= low) & (t <= high), axis=1)
