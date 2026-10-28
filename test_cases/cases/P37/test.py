import pandas as pd
from solution import days_between

out = days_between("2024-01-01", "2024-01-04")
assert [d.strftime("%Y-%m-%d") for d in out] == ["2024-01-01", "2024-01-02", "2024-01-03"]
assert isinstance(out, pd.DatetimeIndex)
print("PASS")
