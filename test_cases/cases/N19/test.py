import numpy as np
from solution import as_reals

out = as_reals([1, 2])
assert out.dtype == np.float64 and out.tolist() == [1.0, 2.0]
arr = as_reals(np.array([3, 4], dtype=np.int32))
assert arr.dtype == np.float64 and arr.tolist() == [3.0, 4.0]
print("PASS")
