# Valid and invalid axes, a repeated axis, axes of the wrong type.
import numpy as np
from solution import safe_sum

arr = np.array([[1, 2], [3, 4]])
for axis in (0, 5, -3, (0, 0), (0, 5), 1.5, "a"):
    try:
        out = safe_sum(arr, axis)
        result = out.tolist() if hasattr(out, "tolist") else out
    except Exception as e:
        result = f"{type(e).__name__}: {e}"
    print(repr(axis), result)
