import pandas as pd
from solution import pick

labels = pd.Categorical(["a", "b", "a"], categories=["a", "b", "c"])
out = pick(labels, [2, 1])
assert list(out) == ["a", "b"]
assert list(out.categories) == ["a", "b", "c"]
print("PASS")
