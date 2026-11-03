# Column labels of different kinds.
import pandas as pd
from solution import has_mixed_labels

for labels in (["region", 2.5], ["region", "sales"], ["a", 1], [1, 2.5], [1, 2], [True, "a"], [1.5, 2.5],
               [None, "a"], [pd.Timestamp("2024-01-01"), "a"]):
    try:
        result = has_mixed_labels(pd.DataFrame([list(range(len(labels)))], columns=labels))
    except Exception as e:
        result = f"{type(e).__name__}: {e}"
    print(labels, result)
