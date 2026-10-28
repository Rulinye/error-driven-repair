import pandas as pd
from solution import weekly_totals

sales = pd.Series(range(1, 11), index=pd.date_range("2024-01-01", periods=10, freq="D"))
out = weekly_totals(sales)
assert list(out.index) == [1, 2]
assert out.tolist() == [28, 27]
assert out.dtype == "int64"
print("PASS")
