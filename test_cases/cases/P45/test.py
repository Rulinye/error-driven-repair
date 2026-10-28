import pandas as pd
from solution import mean_by_team

df = pd.DataFrame({"team": ["A", "A", "B"], "name": ["x", "y", "z"], "score": [10, 20, 30]})
out = mean_by_team(df)
assert list(out.columns) == ["score"]
assert out["score"].to_dict() == {"A": 15.0, "B": 30.0}
assert out["score"].dtype == "float64"
print("PASS")
