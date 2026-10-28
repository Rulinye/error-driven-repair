import numpy as np


def running_best(scores):
    """Return the best score seen so far at each step."""
    best = -np.inf
    out = []
    for s in scores:
        best = max(best, s)
        out.append(best)
    return out
