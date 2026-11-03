# Lists and scalars, float32 and long double reactances, a complex reactance, broadcasting, NaN.
import numpy as np
from solution import impedances

for args in (([1, 2], [3, 4]), (1.5, -2), ([1], [np.float32(0.1)]), ([1], [np.longdouble(0.1)]),
             ([1, 2], [1 + 1j, 0]), ([1, 2], 3), ([1], [np.nan])):
    try:
        out = impedances(*args)
        result = (out.dtype.name, out.tolist())
    except Exception as e:
        result = f"{type(e).__name__}: {e}"
    print(result)
