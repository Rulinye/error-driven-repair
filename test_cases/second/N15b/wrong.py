import numpy as np


def factorials(n):
    """Return the factorials 1!, 2!, ..., n! as an array of integers."""
    return np.prod(np.arange(1, n + 1))
