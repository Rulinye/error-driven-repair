import pandas as pd
from solution import names_above

scores = pd.Series([3.0, 7.5, 9.0], index=["ann", "bob", "cy"])
assert names_above(scores, 5) == ["bob", "cy"]
assert names_above(scores, 10) == []
print("PASS")
