# Missing values, an empty list, a Series with labels, a datetime64[D] array, an early date, a time of day.
import numpy as np
import pandas as pd
from solution import to_dates

for texts in (["2020-01-01", "2021-06-15"], ["2020-01-01", None], [], pd.Series(["2020-01-01"], index=["a"]),
              np.array(["2020-01-01"], dtype="M8[D]"), ["1500-01-01"], ["2020-01-01 10:30"], ("2020-01-01",)):
    try:
        out = to_dates(texts)
        result = (out.dtype.name, out.tolist(), out.index.tolist())
    except Exception as e:
        result = f"{type(e).__name__}: {e}"
    print(result)
