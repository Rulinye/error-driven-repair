from solution import any_type_array

out = any_type_array([1, "a", None])
assert out.dtype == object and out.tolist() == [1, "a", None]
nums = any_type_array([1, 2])
assert nums.dtype == object and nums.tolist() == [1, 2]
print("PASS")
