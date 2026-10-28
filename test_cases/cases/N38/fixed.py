import warnings

import numpy as np


def is_ragged(rows):
    """Return True if the rows differ in length, using NumPy's warning about ragged input."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", np.exceptions.VisibleDeprecationWarning)
        try:
            np.array(rows)
        except (np.exceptions.VisibleDeprecationWarning, ValueError):
            return True
    return False
