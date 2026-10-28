import numpy as np
from solution import cumulative_growth

out = cumulative_growth([0.1, 0.2])
assert np.allclose(out, [1.1, 1.32]) and out.shape == (2,)
print("PASS")
