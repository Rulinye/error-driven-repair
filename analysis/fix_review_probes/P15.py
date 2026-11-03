# Indexes with missing values, integers and a MultiIndex.
import pandas as pd
from solution import labels_as_text

for index in (pd.Index([1.5, 2.0, 10.25]), pd.Index([1.5, None]), pd.Index(["a", None]),
              pd.DatetimeIndex(["2024-03-01 10:00", None]), pd.Index([1, 2]), pd.MultiIndex.from_tuples([(1, "a")])):
    try:
        result = labels_as_text(index)
    except Exception as e:
        result = f"{type(e).__name__}: {e}"
    print(result)
