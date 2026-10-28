import numpy as np
from solution import scalar_type_of

assert scalar_type_of("f8") is np.float64
assert scalar_type_of(np.int32) is np.int32
assert scalar_type_of(np.dtype("u1")) is np.uint8
print("PASS")
