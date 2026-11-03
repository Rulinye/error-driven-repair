import pandas as pd
from solution import billing_months

out = billing_months("2024-01-01", "2024-04-01")
assert [d.strftime("%Y-%m-%d") for d in out] == ["2024-01-01", "2024-02-01", "2024-03-01"]
assert isinstance(out, pd.DatetimeIndex)
print("PASS")
