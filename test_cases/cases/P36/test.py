import pandas as pd
from solution import morning_rows

times = pd.to_datetime(["2024-01-01 07:59", "2024-01-01 08:00", "2024-01-01 10:00", "2024-01-01 12:00"])
out = morning_rows(pd.DataFrame({"event": ["a", "b", "c", "d"]}, index=times))
assert out["event"].tolist() == ["b", "c"]
print("PASS")
