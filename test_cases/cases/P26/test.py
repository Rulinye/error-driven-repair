import pandas as pd
from solution import spread

assert spread(pd.Series([1, 2, 3, 6])) == 1.5
assert spread(pd.Series([1.0, None, 3.0])) == 1.0
print("PASS")
