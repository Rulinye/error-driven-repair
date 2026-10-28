import pandas as pd
from solution import two_hour_totals

readings = pd.Series(range(1, 7), index=pd.date_range("2024-01-01 00:00", periods=6, freq="h"))
out = two_hour_totals(readings)
assert [t.strftime("%d %H:%M") for t in out.index] == ["31 23:00", "01 01:00", "01 03:00", "01 05:00"]
assert out.tolist() == [1, 5, 9, 6]
print("PASS")
