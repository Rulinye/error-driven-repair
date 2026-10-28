import pandas as pd
from solution import long_format

wide = pd.DataFrame({"hr1": [514, 573], "hr2": [545, 526], "team": ["Red", "Blue"],
                     "year1": [2007, 2007], "year2": [2008, 2008]})
out = long_format(wide)
assert out[["team", "year", "hr"]].values.tolist() == [
    ["Red", 2007, 514], ["Blue", 2007, 573], ["Red", 2008, 545], ["Blue", 2008, 526]]
print("PASS")
