from solution import factorials

out = factorials(5)
assert out.tolist() == [1, 2, 6, 24, 120]
assert out.dtype.kind == "i"
print("PASS")
