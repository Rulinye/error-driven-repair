import numpy as np
from solution import mask_negative
out = mask_negative([1, -2, 3])
assert out[0] == 1 and np.isnan(out[1]) and out[2] == 3
print("PASS")
