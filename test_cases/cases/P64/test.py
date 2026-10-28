import pandas as pd
from solution import nearest_month

months = pd.period_range("2024-01", periods=3, freq="M")
assert nearest_month(months, pd.Period("2024-05", freq="M")) == 2
assert nearest_month(months, pd.Period("2024-02", freq="M")) == 1
print("PASS")
