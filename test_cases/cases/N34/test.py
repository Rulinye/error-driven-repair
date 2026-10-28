import numpy as np
from solution import density_histogram

hist, edges = density_histogram([0, 1, 1, 2, 3, 3], 3)
assert np.allclose(hist, [1 / 6, 2 / 6, 3 / 6])
assert edges.tolist() == [0.0, 1.0, 2.0, 3.0]
print("PASS")
