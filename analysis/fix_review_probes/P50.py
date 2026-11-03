# A datetime column, and columns of date strings.
import pandas as pd
from solution import with_datetime_column

for name, df in (("datetimes", pd.DataFrame({"w": pd.to_datetime(["2020-01-01 10:00"]), "n": [1]})),
                 ("date strings", pd.DataFrame({"w": ["2020-01-01", "2021-06-15"], "n": [1, 2]})),
                 ("strings with a time", pd.DataFrame({"w": ["2020-01-01 10:30"], "n": [1]})),
                 ("strings and None", pd.DataFrame({"w": ["2020-01-01", None], "n": [1, 2]}))):
    try:
        out = with_datetime_column(df, "w")
        result = (str(out["w"].dtype), out["w"].tolist())
    except Exception as e:
        result = f"{type(e).__name__}: {e}"
    print(name, result)
