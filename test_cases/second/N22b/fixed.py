import numpy as np


def stacked_dtype(frame):
    """Return the dtype of a NumPy array that can hold all the columns of the table without loss."""
    return np.result_type(*frame.dtypes)
