import pandas as pd
from solution import lunch_orders

times = pd.to_datetime(["2024-05-02 11:29", "2024-05-02 11:30", "2024-05-02 13:59", "2024-05-02 14:00"])
out = lunch_orders(pd.Series([10.0, 12.5, 8.0, 9.5], index=times))
assert out.tolist() == [12.5, 8.0]
print("PASS")
