import pandas as pd
from solution import stamps_as_series

stamps = pd.DatetimeIndex(["2024-05-01 10:00", "2024-05-02 11:30"], tz="Europe/Berlin")
out = stamps_as_series(stamps)
assert str(out.dtype) == "datetime64[ns, Europe/Berlin]"
assert out.index.equals(stamps)
assert list(out) == list(stamps)
print("PASS")
