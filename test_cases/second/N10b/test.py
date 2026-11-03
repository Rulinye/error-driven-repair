import numpy as np
from solution import missing_block

out = missing_block(2, 3)
assert out.shape == (2, 3) and out.dtype == np.float64
assert np.isnan(out).all()
print("PASS")
