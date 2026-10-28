import pandas as pd
from solution import one_day_later

daily = pd.Series([1.0, 2.0, 3.0], index=pd.date_range("2024-01-01", periods=3, freq="D"))
out = one_day_later(daily)
assert list(out.index) == list(pd.date_range("2024-01-02", periods=3, freq="D"))
assert out.tolist() == [1.0, 2.0, 3.0]
print("PASS")
