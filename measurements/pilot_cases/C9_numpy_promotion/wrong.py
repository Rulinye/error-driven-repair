import numpy as np

def add_offset(x):
    return np.float32(x) + np.float32(0.1)  # still float32: precision lost
