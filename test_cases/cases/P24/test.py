import pandas as pd
from solution import float_copy

index = pd.Index([1, 2, 3], name="step")
out = float_copy(index)
assert out.dtype == "float64"
assert out.tolist() == [1.0, 2.0, 3.0]
assert out.name == "step"
assert index.dtype == "int64", "the input index must not change"
print("PASS")
