import pandas as pd
from solution import quarter_hour_counts

times = pd.to_datetime(["2024-01-01 00:06", "2024-01-01 00:19", "2024-01-01 00:21", "2024-01-01 00:40"])
out = quarter_hour_counts(pd.Series([1, 1, 1, 1], index=times))
assert [t.strftime("%H:%M") for t in out.index] == ["00:05", "00:20", "00:35"]
assert out.tolist() == [2, 1, 1]
print("PASS")
