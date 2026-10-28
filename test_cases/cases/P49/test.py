import pandas as pd
from solution import to_dates

out = to_dates(["2020-01-01", "2021-06-15"])
assert out.dtype.kind == "M"
assert out.tolist() == [pd.Timestamp("2020-01-01"), pd.Timestamp("2021-06-15")]
print("PASS")
