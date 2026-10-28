import numpy as np
from solution import is_integer_array

assert bool(is_integer_array(np.array([1], dtype=np.int8))) is True
assert bool(is_integer_array(np.array([1], dtype=np.uint32))) is True
assert bool(is_integer_array(np.array([1.0]))) is False
print("PASS")
