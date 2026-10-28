import numpy as np
from solution import to_dtype

out = to_dtype([1, 2], "f8")
assert out.dtype == np.float64 and out.tolist() == [1.0, 2.0]
ints = to_dtype([1.7, -2.2], "i4")
assert ints.dtype == np.int32 and ints.tolist() == [1, -2]
print("PASS")
