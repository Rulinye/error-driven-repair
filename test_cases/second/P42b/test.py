import pandas as pd
from solution import running_average

out = running_average(pd.Series([4.0, 2.0, 6.0, 8.0]))
assert out.tolist() == [4.0, 3.0, 4.0, 5.0]
assert out.dtype == "float64"
print("PASS")
