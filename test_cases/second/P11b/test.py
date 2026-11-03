import pandas as pd
from solution import add_week_column

visits = pd.DataFrame({"count": [5, 7, 2]}, index=pd.to_datetime(["2024-01-05", "2024-01-08", "2024-03-01"]))
out = add_week_column(visits)
assert out["week"].tolist() == [1, 2, 9]
assert out["count"].tolist() == [5, 7, 2]
assert "week" not in visits.columns, "the input table must not change"
print("PASS")
