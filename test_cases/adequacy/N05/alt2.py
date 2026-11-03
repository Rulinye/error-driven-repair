import numpy as np


def codes_as_text(codes):
    """Return the codes as an array of text labels."""
    return np.array(codes, dtype="U")
