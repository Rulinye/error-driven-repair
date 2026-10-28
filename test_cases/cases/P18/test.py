import pandas as pd
from solution import time_into_month

stamps = pd.DatetimeIndex(["2024-01-15 06:00", "2024-02-01 00:30"])
out = time_into_month(stamps)
assert list(out) == [pd.Timedelta(days=14, hours=6), pd.Timedelta(minutes=30)]
assert out.dtype == "timedelta64[ns]"
print("PASS")
