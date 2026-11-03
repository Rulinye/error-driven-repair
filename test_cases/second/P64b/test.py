import pandas as pd
from solution import closest_quarter

quarters = pd.period_range("2023Q1", periods=4, freq="Q")
assert closest_quarter(quarters, pd.Period("2024Q3", freq="Q")) == 3
assert closest_quarter(quarters, pd.Period("2023Q2", freq="Q")) == 1
print("PASS")
