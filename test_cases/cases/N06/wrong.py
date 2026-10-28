import numpy as np


def normalise(weights):
    """Scale the weights so that they sum to 1, in double precision."""
    w = np.asarray(weights, dtype=np.float16)
    return w / w.sum()
