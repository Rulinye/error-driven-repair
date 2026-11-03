import numpy as np


def empty_buckets(n):
    """Return an array of n empty lists, one per bucket."""
    out = np.empty(n, dtype=np.object)
    for i in range(n):
        out[i] = []
    return out
