import pandas as pd
from solution import daily_totals_at_end

times = pd.to_datetime(["2024-03-01 09:00", "2024-03-01 17:30", "2024-03-02 08:15"])
out = daily_totals_at_end(pd.Series([10, 5, 7], index=times))
assert [t.strftime("%m-%d %H:%M") for t in out.index] == ["03-02 00:00", "03-03 00:00"]
assert out.tolist() == [15, 7]
print("PASS")
