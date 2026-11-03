# Arrays of every kind of dtype.
import numpy as np
from solution import is_integer_array

for arr in (np.array([1], dtype=np.int8), np.array([1], dtype=np.uint64), np.array([1.0]), np.array([True]),
            np.array([1], dtype="m8[s]"), np.array([1], dtype="M8[s]"), np.array(["a"]),
            np.array([1], dtype=object), np.array([1 + 1j])):
    try:
        result = is_integer_array(arr)
    except Exception as e:
        result = f"{type(e).__name__}: {e}"
    print(arr.dtype, result)
