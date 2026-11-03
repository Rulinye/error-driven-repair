# Integer and float values, with and without a limit, NaN, a smaller dtype, a scalar.
import numpy as np
from solution import clip_upper

for args in (([1, 5],), ([1, 5], 3), ([1, 5], 2.5), ([1.0, 5.0],), ([1.0, np.nan], 3), ([1, 5], np.nan),
             (np.array([1, 5], dtype=np.int8), 3), (np.array([1, 5], dtype=np.float32),), (4,)):
    try:
        out = np.asarray(clip_upper(*args))
        result = (out.dtype.name, out.tolist())
    except Exception as e:
        result = f"{type(e).__name__}: {e}"
    print(args, result)
