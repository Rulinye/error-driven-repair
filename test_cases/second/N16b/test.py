from solution import rows_within

out = rows_within([[1, 2, 3], [0, 5, 9]], 1, 8)
assert out.tolist() == [True, False]
print("PASS")
