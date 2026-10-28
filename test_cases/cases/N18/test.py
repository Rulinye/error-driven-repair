import numpy as np
from solution import round_prices

out = round_prices(np.array([2.499, 3.14159, 10.0]))
assert out.tolist() == [2.5, 3.14, 10.0]
assert out.dtype == np.float64
print("PASS")
