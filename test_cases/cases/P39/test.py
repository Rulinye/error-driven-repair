from solution import encode

codes, uniques = encode(["b", None, "a", "b"])
assert codes.tolist() == [0, -1, 1, 0]
assert list(uniques) == ["b", "a"]
print("PASS")
