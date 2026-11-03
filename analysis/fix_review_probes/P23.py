# Is the result the input table, does it share its data, and is a wrong number of names rejected?
import pandas as pd
from solution import rename_columns

df = pd.DataFrame({"c0": [1, 2], "c1": [0.5, 1.5]})
out = rename_columns(df, ["count", "share"])
print("result columns", list(out.columns), "| result is the input", out is df, "| input columns", list(df.columns))
out.iloc[0, 0] = 99
print("input value after writing to the result:", df.iloc[0, 0])
try:
    rename_columns(pd.DataFrame({"a": [1]}), ["x", "y"])
    print("two names for one column: accepted")
except Exception as e:
    print("two names for one column:", type(e).__name__)
