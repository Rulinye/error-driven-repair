import pandas as pd
from solution import never_decreases

assert never_decreases(pd.Series([1, 2, 2, 5])) is True
assert never_decreases(pd.Series([1, 3, 2, 5])) is False
print("PASS")
