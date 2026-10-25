import numpy as np
from solution import to_float_array
out = to_float_array([1, 2, 3])
assert out.dtype == np.float64
assert out.tolist() == [1.0, 2.0, 3.0]
print("PASS")
