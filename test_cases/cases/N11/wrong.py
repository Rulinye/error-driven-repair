import numpy as np


def nearest_distance(points, target):
    """Return the smallest distance from the target to any of the points (infinity if there are none)."""
    best = np.Infinity
    for p in points:
        best = min(best, abs(p - target))
    return best
