import numpy as np
from solution import bytes_needed

assert bytes_needed(10, np.float64) == 80
assert bytes_needed(3, np.int16) == 6
print("PASS")
