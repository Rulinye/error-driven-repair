import pandas as pd
from solution import in_time_order

times = pd.to_datetime(["2024-01-01 08:00", "2024-01-01 09:00", "2024-01-01 09:00"])
assert in_time_order(pd.DataFrame({"x": [1, 2, 3]}, index=times)) is True
shuffled = pd.to_datetime(["2024-01-01 09:00", "2024-01-01 08:00", "2024-01-01 10:00"])
assert in_time_order(pd.DataFrame({"x": [1, 2, 3]}, index=shuffled)) is False
print("PASS")
