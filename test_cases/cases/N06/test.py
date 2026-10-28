import numpy as np
from solution import normalise

out = normalise([1, 1, 2])
assert out.dtype == np.float64
assert out.tolist() == [0.25, 0.25, 0.5]
print("PASS")
