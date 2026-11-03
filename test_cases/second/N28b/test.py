import numpy as np
from solution import zero_of

assert type(zero_of("f4")) is np.float32 and zero_of("f4") == 0
assert type(zero_of(np.int16)) is np.int16
assert type(zero_of(np.dtype("u8"))) is np.uint64
print("PASS")
