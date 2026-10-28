from solution import read_skipping_bad_lines

out = read_skipping_bad_lines("a,b\n1,2\n3,4,5\n6,7\n")
assert out.values.tolist() == [[1, 2], [6, 7]]
assert list(out.columns) == ["a", "b"]
print("PASS")
