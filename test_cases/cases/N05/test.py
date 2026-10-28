from solution import codes_as_text

out = codes_as_text([1, 22, 333])
assert out.dtype.kind == "U"
assert out.tolist() == ["1", "22", "333"]
print("PASS")
