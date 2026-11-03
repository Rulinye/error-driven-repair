# The test table, a table whose other columns repeat, and a table with a missing value.
import pandas as pd
from solution import long_format

for wide in (pd.DataFrame({"hr1": [514, 573], "hr2": [545, 526], "team": ["Red", "Blue"],
                           "year1": [2007, 2007], "year2": [2008, 2008]}),
             pd.DataFrame({"hr1": [514, 573], "hr2": [545, None], "team": ["Red", "Red"],
                           "year1": [2007, 2007], "year2": [2008, 2008]}),
             pd.DataFrame({"hr1": [514, 573], "hr2": [545, None], "team": ["Red", "Blue"],
                           "year1": [2007, 2007], "year2": [2008, 2008]})):
    try:
        result = long_format(wide).to_dict("list")
    except Exception as e:
        result = f"{type(e).__name__}: {e}"
    print(result)
