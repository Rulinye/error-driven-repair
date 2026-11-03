import numpy as np


def unit_circle(n):
    """Return n points evenly spaced on the unit circle, as double-precision complex numbers."""
    out = np.zeros(n, dtype=np.complex_)
    for k in range(n):
        out[k] = np.exp(2j * np.pi * k / n)
    return out
