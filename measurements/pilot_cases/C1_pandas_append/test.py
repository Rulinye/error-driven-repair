import pandas as pd
from solution import add_row
df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
out = add_row(df, {"a": 3, "b": "z"})
assert out["a"].tolist() == [1, 2, 3]
assert out["b"].tolist() == ["x", "y", "z"]
assert len(df) == 2, "input DataFrame must not be modified"
print("PASS")
