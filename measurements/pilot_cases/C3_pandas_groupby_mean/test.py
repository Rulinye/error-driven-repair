import pandas as pd
from solution import mean_by_team
df = pd.DataFrame({"team": ["A", "A", "B"], "name": ["x", "y", "z"], "score": [10, 20, 30]})
out = mean_by_team(df)
assert list(out.columns) == ["score"]
assert out.loc["A", "score"] == 15 and out.loc["B", "score"] == 30
print("PASS")
