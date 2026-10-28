from solution import any_missing

assert any_missing([1.0, float("nan")]) is True
assert any_missing([1.0, 2.0]) is False
print("PASS")
