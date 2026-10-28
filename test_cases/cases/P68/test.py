from solution import single_label

out = single_label("gold")
assert list(out) == ["gold"]
assert list(out.categories) == ["gold"]
print("PASS")
