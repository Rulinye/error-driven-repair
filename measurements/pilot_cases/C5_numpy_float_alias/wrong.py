import numpy as np

def to_float_array(xs):
    return np.array(xs, dtype=np.float32)  # plausible fix, but changes precision
