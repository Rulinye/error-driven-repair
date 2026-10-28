import pandas as pd
from solution import total_per_store

sales = pd.DataFrame({"store": ["b", "a", "b"], "amount": [5, 2, 4]})
out = total_per_store(sales)
assert out.to_dict() == {"a": 2, "b": 9}
assert out.dtype == "int64"
one = total_per_store(pd.DataFrame({"store": ["a", "a"], "amount": [1, 2]}))
assert isinstance(one, pd.Series) and one.to_dict() == {"a": 3}
print("PASS")
