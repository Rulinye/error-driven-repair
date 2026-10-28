import pandas as pd
from solution import labels_as_text

out = labels_as_text(pd.Index([1.5, 2.0, 10.25]))
assert out == ["1.5", "2.0", "10.25"]
assert all(isinstance(x, str) for x in out)
days = labels_as_text(pd.DatetimeIndex(["2024-03-01", "2024-03-02"]))
assert days == ["2024-03-01", "2024-03-02"]
print("PASS")
