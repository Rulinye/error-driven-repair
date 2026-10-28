import numpy as np


def bytes_needed(n, scalar_type):
    """Return the number of bytes needed to store n values of the given scalar type."""
    return n * np.nbytes[scalar_type]
