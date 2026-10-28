from solution import readings_series

out = readings_series([1.5, 2.0, 0.25])
assert out.tolist() == [1.5, 2.0, 0.25]
assert out.dtype == "float64"
print("PASS")
