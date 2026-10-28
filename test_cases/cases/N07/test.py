import numpy as np
from solution import as_complex

out = as_complex([1, 2.5, 3j])
assert out.dtype == np.complex128
assert out.tolist() == [1 + 0j, 2.5 + 0j, 3j]
print("PASS")
