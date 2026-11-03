import pandas as pd
from solution import unsigned_order_numbers

orders = pd.DataFrame({"qty": [1, 4]}, index=pd.Index([1001, 1002], name="order"))
out = unsigned_order_numbers(orders)
assert out.dtype == "uint64"
assert out.tolist() == [1001, 1002]
assert out.name == "order"
assert orders.index.dtype == "int64", "the input table must not change"
print("PASS")
