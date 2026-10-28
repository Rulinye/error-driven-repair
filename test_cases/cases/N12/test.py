from solution import clip_upper

assert clip_upper([1, 5], 3).tolist() == [1, 3]
assert clip_upper([1, 5]).tolist() == [1.0, 5.0]
print("PASS")
