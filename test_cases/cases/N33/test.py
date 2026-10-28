import numpy as np
from solution import swap_byte_order

arr = np.array([1, 2], dtype="<i4")
out = swap_byte_order(arr)
assert out.dtype.byteorder == ">"
assert out.tolist() == [16777216, 33554432]
assert np.shares_memory(out, arr)
print("PASS")
