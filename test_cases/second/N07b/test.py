import numpy as np
from solution import unit_circle

out = unit_circle(4)
assert out.dtype == np.complex128
assert np.allclose(out, [1, 1j, -1, -1j])
print("PASS")
