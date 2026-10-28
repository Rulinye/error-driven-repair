import numpy as np
from solution import safe_sum

arr = np.array([[1, 2], [3, 4]])
assert safe_sum(arr, 0).tolist() == [4, 6]
assert safe_sum(arr, 5) is None
print("PASS")
