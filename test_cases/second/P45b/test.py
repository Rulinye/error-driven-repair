import pandas as pd
from solution import median_by_region

sales = pd.DataFrame({"region": ["n", "s", "n", "n"], "rep": ["a", "b", "c", "d"], "units": [4, 9, 6, 20]})
out = median_by_region(sales)
assert list(out.columns) == ["units"]
assert out["units"].to_dict() == {"n": 6.0, "s": 9.0}
assert out["units"].dtype == "float64"
print("PASS")
