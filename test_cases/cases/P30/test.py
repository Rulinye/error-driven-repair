import pandas as pd
from solution import total_by_region

index = pd.MultiIndex.from_tuples([("north", "a"), ("north", "b"), ("south", "c")], names=["region", "city"])
out = total_by_region(pd.Series([1, 2, 4], index=index))
assert out.to_dict() == {"north": 3, "south": 4}
assert out.index.name == "region"
assert out.dtype == "int64"
print("PASS")
