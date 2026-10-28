import numpy as np
from solution import impedances

out = impedances([1, 2], [3, 4])
assert out.dtype == np.complex128
assert out.tolist() == [1 + 3j, 2 + 4j]
print("PASS")
