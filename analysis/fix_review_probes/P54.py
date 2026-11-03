# Names, no other indexes, unsorted and repeated days, time zones, a list instead of an index.
import pandas as pd
from solution import all_trading_days


def days(start, n, **kw):
    return pd.date_range(start, periods=n, **kw)


for first, others in ((days("2024-01-01", 2), [days("2024-01-05", 2), days("2024-01-02", 2)]),
                      (days("2024-01-01", 2, name="t"), [days("2024-01-05", 2, name="t")]),
                      (days("2024-01-01", 2, name="t"), [days("2024-01-05", 2, name="u")]),
                      (days("2024-01-01", 2), []),
                      (pd.DatetimeIndex(["2024-01-03", "2024-01-01"]), [pd.DatetimeIndex(["2024-01-02"])]),
                      (pd.DatetimeIndex(["2024-01-01", "2024-01-01"]), [pd.DatetimeIndex(["2024-01-01"])]),
                      (days("2024-01-01", 2, tz="UTC"), [days("2024-01-01 05:00", 2, tz="Asia/Seoul")]),
                      (days("2024-01-01", 2), [["2024-01-09"]])):
    try:
        out = all_trading_days(first, others)
        result = (type(out).__name__, [str(x) for x in out], out.name, str(out.dtype))
    except Exception as e:
        result = f"{type(e).__name__}: {e}"
    print(result)
