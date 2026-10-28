import numpy as np


def clip_upper(values, limit=None):
    """Clip the values at the limit; without a limit, nothing is clipped."""
    upper = np.inf if limit is None else limit
    return np.minimum(values, upper)
