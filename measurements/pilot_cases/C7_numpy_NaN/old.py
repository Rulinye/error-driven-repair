import numpy as np

def mask_negative(xs):
    arr = np.array(xs, dtype=float)
    arr[arr < 0] = np.NaN
    return arr
