import numpy as np
import pandas as pd
from solution import stacked_dtype

frame = pd.DataFrame({"a": np.array([1], dtype=np.int32), "b": np.array([1.5], dtype=np.float32)})
assert stacked_dtype(frame) == np.dtype("float64")
frame = pd.DataFrame({"a": np.array([1], dtype=np.int8), "b": np.array([1], dtype=np.uint8)})
assert stacked_dtype(frame) == np.dtype("int16")
frame = pd.DataFrame({"a": [True], "b": np.array([1], dtype=np.int64)})
assert stacked_dtype(frame) == np.dtype("int64")
print("PASS")
