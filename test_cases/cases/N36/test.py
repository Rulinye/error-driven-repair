import numpy as np
from solution import shifted_level

assert shifted_level(np.uint8(1), 300) == 301
assert shifted_level(np.uint8(255), 1000) == 1255
print("PASS")
