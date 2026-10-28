import numpy as np


def as_complex(values):
    """Return the values as an array of double-precision complex numbers."""
    return np.asarray(values, dtype=np.complex64)
