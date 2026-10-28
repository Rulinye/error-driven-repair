import numpy as np


def bucket_numbers(values, width):
    """Return the number of the bucket of each value, for buckets of the given width."""
    return (np.asarray(values) // width).astype(np.int8)
