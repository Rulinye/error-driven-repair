import pandas as pd
from solution import make_index
idx = make_index([3, 1, 2])
assert isinstance(idx, pd.Index) and str(idx.dtype) == "int64"
assert list(idx) == [3, 1, 2]
print("PASS")
