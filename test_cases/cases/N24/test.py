import numpy as np
from solution import is_float_type

assert is_float_type(np.float32) is True
assert is_float_type(np.float64) is True
assert is_float_type(np.int64) is False
print("PASS")
