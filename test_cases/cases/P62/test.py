import pandas as pd
from solution import week_numbers

stamps = pd.array(pd.to_datetime(["2024-01-07", "2024-01-08", "2024-12-30"]))
assert week_numbers(stamps) == [1, 2, 1]
print("PASS")
