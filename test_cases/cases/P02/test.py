import pandas as pd
from solution import all_readings

morning = pd.Series([1.5, 2.0])
evening = pd.Series([2.5])
out = all_readings(morning, evening)
assert out.tolist() == [1.5, 2.0, 2.5]
assert out.index.tolist() == [0, 1, 2]
assert out.dtype == "float64"
print("PASS")
