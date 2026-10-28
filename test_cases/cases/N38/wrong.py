import warnings

import numpy as np


def is_ragged(rows):
    """Return True if the rows differ in length, using NumPy's warning about ragged input."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", np.complexfloating)
        try:
            np.array(rows)
        except (np.complexfloating, ValueError):
            return True
    return False
