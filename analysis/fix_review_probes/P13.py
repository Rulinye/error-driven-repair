# Categoricals of text, integers, missing values and datetimes.
import pandas as pd
from solution import plain_values

for cat in (pd.Categorical(["B", "A", "B"], categories=["A", "B", "C"]), pd.Categorical([3, 1, 3]),
            pd.Categorical([3, None, 1]), pd.Categorical(["a", None]),
            pd.Categorical(pd.to_datetime(["2024-01-01", None])), pd.Categorical([1.5, 2.5], ordered=True)):
    try:
        out = plain_values(cat)
        result = (type(out).__name__, out.dtype.name, out.tolist())
    except Exception as e:
        result = f"{type(e).__name__}: {e}"
    print(result)
