import numpy as np
from solution import precise_sum

out = precise_sum([0.5, 0.25, 2.0])
assert out.dtype == np.longdouble
assert float(out) == 2.75
print("PASS")
