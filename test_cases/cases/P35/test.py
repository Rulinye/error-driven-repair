import pandas as pd
from solution import hourly_means

readings = pd.Series([1.0, 2.0, 3.0, 4.0], index=pd.date_range("2024-01-01 00:00", periods=4, freq="30min"))
out = hourly_means(readings)
assert [t.strftime("%H:%M") for t in out.index] == ["01:00", "02:00"]
assert out.tolist() == [1.5, 3.5]
print("PASS")
