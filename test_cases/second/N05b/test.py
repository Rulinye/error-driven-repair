from solution import zero_padded

out = zero_padded([7, 42, 123], 3)
assert out.dtype.kind == "U"
assert out.tolist() == ["007", "042", "123"]
print("PASS")
