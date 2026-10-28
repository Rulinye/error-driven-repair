import pandas as pd
from solution import in_range

out = in_range(pd.Series([1.0, 2.0, 3.0]), 1.0, 2.0)
assert out.tolist() == [True, True, False]
assert out.dtype == bool
print("PASS")
