from solution import empty_buckets

out = empty_buckets(3)
assert out.dtype == object and out.shape == (3,)
assert all(b == [] for b in out)
out[0].append(1)
assert out[1] == [], "the lists must be separate"
print("PASS")
