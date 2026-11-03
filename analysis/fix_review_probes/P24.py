# Indexes of integers, floats, text and a RangeIndex.
import pandas as pd
from solution import float_copy

for index in (pd.Index([1, 2, 3], name="step"), pd.Index([1.5, 2.0]), pd.Index(["1", "2"]), pd.RangeIndex(3, name="r")):
    try:
        out = float_copy(index)
        result = (out.dtype.name, out.tolist(), out.name, out is index)
    except Exception as e:
        result = f"{type(e).__name__}: {e}"
    print(result)
