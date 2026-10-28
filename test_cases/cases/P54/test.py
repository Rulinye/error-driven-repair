import pandas as pd
from solution import all_trading_days

first = pd.date_range("2024-01-01", periods=2)
others = [pd.date_range("2024-01-05", periods=2), pd.date_range("2024-01-02", periods=2)]
out = all_trading_days(first, others)
assert [d.strftime("%m-%d") for d in out] == ["01-01", "01-02", "01-03", "01-05", "01-06"]
assert isinstance(out, pd.DatetimeIndex)
print("PASS")
