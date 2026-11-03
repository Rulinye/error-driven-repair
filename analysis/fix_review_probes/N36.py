# Python int offsets, a NumPy int64 offset, fractional offsets, a NumPy uint8 offset.
import numpy as np
from solution import shifted_level

for level, offset in ((np.uint8(1), 300), (np.uint8(255), 1), (np.uint8(5), -10), (np.uint8(5), np.int64(300)),
                      (np.uint8(5), 2.5), (np.uint8(5), -0.5), (np.uint8(250), np.uint8(10))):
    try:
        out = shifted_level(level, offset)
        result = (out, type(out).__name__)
    except Exception as e:
        result = f"{type(e).__name__}: {e}"
    print(repr(level), repr(offset), result)
