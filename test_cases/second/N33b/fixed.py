import numpy as np


def read_big_endian(buffer):
    """Interpret the bytes as big-endian 16-bit unsigned integers and return them as a list of ints."""
    arr = np.frombuffer(buffer, dtype="<u2")
    return arr.view(arr.dtype.newbyteorder()).tolist()
