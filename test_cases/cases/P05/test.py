from solution import customer_index

out = customer_index([3.0, 1.0, 2.0])
assert out.dtype == "int64"
assert out.tolist() == [3, 1, 2]
assert out.name == "customer_id"
print("PASS")
