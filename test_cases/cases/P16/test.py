import pandas as pd
from solution import has_mixed_labels

assert has_mixed_labels(pd.DataFrame([[1, 2]], columns=["region", 2.5])) is True
assert has_mixed_labels(pd.DataFrame([[1, 2]], columns=["region", "sales"])) is False
print("PASS")
