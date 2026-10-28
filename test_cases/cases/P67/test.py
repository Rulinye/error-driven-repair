import pandas as pd
from solution import index_by_id

out = index_by_id(pd.DataFrame({"id": [7, 3], "score": [0.5, 0.9]}))
assert out.index.tolist() == [7, 3]
assert list(out.columns) == ["id", "score"]
assert out["id"].tolist() == [7, 3]
print("PASS")
