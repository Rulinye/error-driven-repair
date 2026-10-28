from solution import checksum_index

out = checksum_index([7, 2, 9])
assert out.dtype == "uint64"
assert out.tolist() == [7, 2, 9]
print("PASS")
