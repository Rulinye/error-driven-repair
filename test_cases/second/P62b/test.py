import pandas as pd
from solution import busiest_week

stamps = pd.array(pd.to_datetime(["2024-01-02", "2024-01-15", "2024-01-16", "2024-01-17", "2024-02-01"]))
assert busiest_week(stamps) == 3
print("PASS")
