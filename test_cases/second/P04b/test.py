import pandas as pd
from solution import as_pairs

prices = pd.Series([1.5, 20.0, 3.25], index=["tea", "cake", "milk"])
assert as_pairs(prices) == ["tea=1.5", "cake=20", "milk=3.25"]
print("PASS")
