from solution import price_levels

out = price_levels([10, 20, 30])
assert out.dtype == "float64"
assert out.tolist() == [10.0, 20.0, 30.0]
assert out.name == "price"
print("PASS")
