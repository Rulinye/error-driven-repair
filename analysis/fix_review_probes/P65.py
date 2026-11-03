# Unsorted groups, missing values, a single-level index, a missing group label, no level named "group".
import numpy as np
import pandas as pd
from solution import sem_per_group


def levels(tuples):
    return pd.MultiIndex.from_tuples(tuples, names=["group", "i"])


for values in (pd.Series([1.0, 2.0, 4.0, 6.0], index=levels([("a", 1), ("a", 2), ("b", 1), ("b", 2)])),
               pd.Series([1.0, np.nan, 4.0], index=levels([("b", 1), ("b", 2), ("a", 1)])),
               pd.Series([1.0, 3.0], index=pd.Index(["x", "x"], name="group")),
               pd.Series([1.0, 3.0], index=levels([(np.nan, 1), ("a", 2)])),
               pd.Series([1, 3], index=pd.Index(["x", "y"], name="g"))):
    try:
        out = sem_per_group(values)
        result = (out.to_dict(), out.index.name)
    except Exception as e:
        result = f"{type(e).__name__}: {e}"
    print(result)
