import pandas as pd
from solution import clip_negatives

out = clip_negatives(pd.Series([1.5, -2.0, 3.0]))
assert out.tolist() == [1.5, 0.0, 3.0]
assert out.dtype == "float64"
print("PASS")
