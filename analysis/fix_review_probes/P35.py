# Regular and irregular readings, a time zone with a clock change, an empty series and a table.
import pandas as pd
from solution import hourly_means

half_hours = pd.date_range("2024-01-01 00:00", periods=4, freq="30min")
irregular = pd.to_datetime(["2024-01-01 00:10", "2024-01-01 02:59", "2024-01-01 03:00"])
for data in (pd.Series([1.0, 2.0, 3.0, 4.0], index=half_hours),
             pd.Series([1.0, 2.0, 3.0], index=irregular),
             pd.Series([1.0, 2.0], index=pd.date_range("2024-03-31 00:30", periods=2, freq="h", tz="Europe/Berlin")),
             pd.Series([], dtype=float, index=pd.DatetimeIndex([])),
             pd.DataFrame({"a": [1.0, 2.0]}, index=half_hours[:2])):
    try:
        out = hourly_means(data)
        result = ([str(t) for t in out.index], out.values.tolist())
    except Exception as e:
        result = f"{type(e).__name__}: {e}"
    print(result)
