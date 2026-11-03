import pandas as pd
from solution import cap_values

out = cap_values(pd.Series([3, 12, 7, 25]), 10)
assert out.tolist() == [3, 10, 7, 10]
assert out.dtype == "int64"
print("PASS")
