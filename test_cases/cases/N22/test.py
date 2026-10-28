import numpy as np
from solution import common_dtype

a = np.array([1], dtype=np.int32)
b = np.array([1.5], dtype=np.float32)
assert common_dtype([a, b]) == np.dtype("float64")
c = np.array([1], dtype=np.int8)
d = np.array([1], dtype=np.uint8)
assert common_dtype([c, d]) == np.dtype("int16")
print("PASS")
