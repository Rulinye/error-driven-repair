import pandas as pd
from solution import add_week

visits = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-01-09", "2024-12-30"]),
                       "patient": ["a", "b", "c"]})
out = add_week(visits)
assert out["week"].tolist() == [1, 2, 1]
assert out["week"].dtype.kind in "iu"
assert out["patient"].tolist() == ["a", "b", "c"]
assert "week" not in visits.columns, "the input table must not change"
print("PASS")
