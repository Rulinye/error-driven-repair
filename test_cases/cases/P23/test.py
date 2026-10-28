import pandas as pd
from solution import rename_columns

df = pd.DataFrame({"c0": [1, 2], "c1": [0.5, 1.5]})
out = rename_columns(df, ["count", "share"])
assert list(out.columns) == ["count", "share"]
assert out["count"].tolist() == [1, 2] and out["share"].dtype == "float64"
print("PASS")
