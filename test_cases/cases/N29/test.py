import numpy as np
from solution import type_code

assert type_code(np.float64) == "d"
assert type_code(np.int8) == "b"
assert type_code(np.complex64) == "F"
print("PASS")
