from solution import encode_tags

out = encode_tags(["ab", "c"])
assert out.dtype.kind == "S"
assert out.tolist() == [b"ab", b"c"]
print("PASS")
