import pandas as pd
from solution import sem_per_group

index = pd.MultiIndex.from_tuples([("a", 1), ("a", 2), ("b", 1), ("b", 2)], names=["group", "i"])
out = sem_per_group(pd.Series([1.0, 2.0, 4.0, 6.0], index=index))
assert out.round(12).to_dict() == {"a": 0.5, "b": 1.0}
assert out.index.name == "group"
print("PASS")
