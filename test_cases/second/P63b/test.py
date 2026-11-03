import pandas as pd
from solution import stores_with_returns

index = pd.MultiIndex.from_tuples([("s1", "mon"), ("s1", "tue"), ("s2", "mon")], names=["store", "day"])
returns = pd.DataFrame({"toys": [0, 2, 0], "books": [0, 0, 0]}, index=index)
out = stores_with_returns(returns)
assert out.to_dict() == {"toys": {"s1": True, "s2": False}, "books": {"s1": False, "s2": False}}
print("PASS")
