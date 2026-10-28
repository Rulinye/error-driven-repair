import pandas as pd
from solution import column_spread

out = column_spread(pd.DataFrame({"a": [1, 2, 3, 6], "b": [0.0, 0.0, 1.0, 1.0]}))
assert out.to_dict() == {"a": 1.5, "b": 0.5}
assert out.dtype == "float64"
print("PASS")
