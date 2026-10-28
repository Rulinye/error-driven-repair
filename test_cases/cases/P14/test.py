import pandas as pd
from solution import most_common_sizes

order = ["S", "M", "L"]
assert most_common_sizes(pd.Categorical(["M", "L", "M", "S"], categories=order)) == ["M"]
assert most_common_sizes(pd.Categorical(["L", "S", "L", "S"], categories=order)) == ["S", "L"]
print("PASS")
