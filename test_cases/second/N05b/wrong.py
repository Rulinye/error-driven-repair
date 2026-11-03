import numpy as np


def zero_padded(numbers, width):
    """Return the numbers as text, padded with zeros on the left to the given width."""
    return np.char.zfill(np.asarray(numbers).astype(np.bytes_), width)
