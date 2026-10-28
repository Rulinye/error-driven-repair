import pandas as pd
from solution import with_levels

out = with_levels(pd.Categorical(["good", "bad", "good"]), ["bad", "ok", "good"])
assert list(out.categories) == ["bad", "ok", "good"]
assert list(out) == ["good", "bad", "good"]
assert out.codes.tolist() == [2, 0, 2]
print("PASS")
