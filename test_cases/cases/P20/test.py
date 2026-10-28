import pandas as pd
from solution import summary_text

pd.set_option("display.max_info_rows", 2)
df = pd.DataFrame({"a": [1.0, None, 3.0], "b": ["x", "y", None]})
out = summary_text(df)
assert "Non-Null Count" in out
assert "2 non-null" in out
assert "float64" in out and "object" in out
print("PASS")
