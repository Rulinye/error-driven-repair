import numpy as np
from solution import to_real_array

out = to_real_array(["1", 2, 3.1])
assert out.dtype == np.float64
assert out.tolist() == [1.0, 2.0, 3.1]
print("PASS")
