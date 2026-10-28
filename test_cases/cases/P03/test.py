import pandas as pd
from solution import column_ranges

df = pd.DataFrame({"city": ["a", "b", "c"], "temp": [20.5, 25.0, 22.0], "rain": [0, 3, 1]})
out = column_ranges(df)
assert out == {"temp": 4.5, "rain": 3}
assert list(out) == ["temp", "rain"]
print("PASS")
