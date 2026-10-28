import pandas as pd
from solution import add_order

orders = pd.DataFrame({"item": ["pen", "ink"], "qty": [3, 1]})
out = add_order(orders, {"item": "pad", "qty": 2})
assert out["item"].tolist() == ["pen", "ink", "pad"]
assert out["qty"].tolist() == [3, 1, 2]
assert out["qty"].dtype == "int64"
assert out.index.tolist() == [0, 1, 2]
assert len(orders) == 2, "the input table must not change"
print("PASS")
