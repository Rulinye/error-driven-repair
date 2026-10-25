import numpy as np
from solution import as_float
out = as_float([1, 2])
assert out.dtype == np.float64 and out.tolist() == [1.0, 2.0]
print("PASS")
