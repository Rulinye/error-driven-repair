import pandas as pd
from solution import running_max

out = running_max(pd.Series([2, 1, 5, 3]))
assert out.tolist() == [2.0, 2.0, 5.0, 5.0]
assert out.dtype == "float64"
print("PASS")
