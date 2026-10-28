import numpy as np
from solution import bucket_numbers

out = bucket_numbers([0.5, 12.0, 29.9, 1000.0], 10)
assert out.dtype == np.int64
assert out.tolist() == [0, 1, 2, 100]
assert bucket_numbers([5000.0], 10).tolist() == [500]
print("PASS")
