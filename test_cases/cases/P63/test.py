import pandas as pd
from solution import any_flag_per_site

index = pd.MultiIndex.from_tuples([("x", 1), ("x", 2), ("y", 1)], names=["site", "day"])
flags = pd.DataFrame({"rain": [False, True, False], "frost": [False, False, True]}, index=index)
out = any_flag_per_site(flags)
assert out.to_dict() == {"rain": {"x": True, "y": False}, "frost": {"x": False, "y": True}}
assert out["rain"].dtype == bool
print("PASS")
