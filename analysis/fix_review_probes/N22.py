# One, two and three arrays; text and datetime dtypes.
import numpy as np
from solution import common_dtype

for codes in (("i4", "f4"), ("i1", "u1"), ("i8",), ("i1", "i2", "f2"), ("u8", "i8"), ("S3", "U2"),
              ("M8[s]", "M8[D]"), ("f2", "i2")):
    try:
        result = common_dtype([np.array([1], dtype=c) for c in codes])
    except Exception as e:
        result = f"{type(e).__name__}: {e}"
    print(codes, result)
