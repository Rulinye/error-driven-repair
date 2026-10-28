import numpy as np
import pandas as pd
from solution import plain_values

out = plain_values(pd.Categorical(["B", "A", "B"], categories=["A", "B", "C"]))
assert isinstance(out, np.ndarray)
assert out.tolist() == ["B", "A", "B"]
assert out.dtype == object
nums = plain_values(pd.Categorical([3, 1, 3]))
assert nums.tolist() == [3, 1, 3] and nums.dtype == "int64"
print("PASS")
