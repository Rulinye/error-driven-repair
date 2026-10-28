import pandas as pd
from solution import with_datetime_column

df = pd.DataFrame({"when": pd.to_datetime(["2020-01-01 10:00", "2020-03-05 23:59"]), "n": [1, 2]})
out = with_datetime_column(df, "when")
assert out["when"].dtype.kind == "M"
assert out["when"].tolist() == [pd.Timestamp("2020-01-01 10:00"), pd.Timestamp("2020-03-05 23:59")]
assert out["n"].tolist() == [1, 2]
print("PASS")
