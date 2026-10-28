import math
from solution import growth_factor

out = growth_factor([0.1, 0.2])
assert math.isclose(float(out), 1.32)
assert getattr(out, "ndim", 0) == 0
print("PASS")
