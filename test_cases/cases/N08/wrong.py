import numpy as np


def encode_tags(tags):
    """Return the tags as an array of byte strings, for writing to a binary file."""
    return np.array(tags, dtype=np.str_)
