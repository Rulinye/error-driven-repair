import pandas as pd
from solution import labels_need_cleaning

assert labels_need_cleaning(pd.Series([1, 2, 3], index=["north", 1.5, "south"])) is True
assert labels_need_cleaning(pd.Series([1, 2], index=["north", "south"])) is False
assert labels_need_cleaning(pd.Series([1, 2], index=[0.5, 1.5])) is False
print("PASS")
