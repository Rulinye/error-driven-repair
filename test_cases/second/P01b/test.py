import pandas as pd
from solution import with_total_row

report = pd.DataFrame({"units": [12, 30], "revenue": [240, 450]}, index=["jan", "feb"])
out = with_total_row(report)
assert out.index.tolist() == ["jan", "feb", "total"]
assert out["units"].tolist() == [12, 30, 42]
assert out["revenue"].tolist() == [240, 450, 690]
assert out["units"].dtype == "int64"
assert len(report) == 2, "the input table must not change"
print("PASS")
