import pandas as pd
from solution import column_max
df = pd.DataFrame({"a": [1, 5, 3], "b": [2.5, 0.5, 9.0]})
assert column_max(df) == {"a": 5, "b": 9.0}
print("PASS")
