import numpy as np


def common_dtype(arrays):
    """Return the dtype that all the given arrays can be safely cast to."""
    return np.common_type(*arrays)
