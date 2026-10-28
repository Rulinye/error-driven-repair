import pandas as pd
from solution import date_summary

events = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-01-03", "2024-01-08"])})
out = date_summary(events)
assert list(out.index) == ["count", "mean", "min", "25%", "50%", "75%", "max"]
assert out["count"] == 3
assert out["mean"] == pd.Timestamp("2024-01-04")
assert out["max"] == pd.Timestamp("2024-01-08")
print("PASS")
