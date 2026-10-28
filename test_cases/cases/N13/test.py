from solution import running_best

assert running_best([3, 1, 5]) == [3, 3, 5]
assert running_best([-5, -7]) == [-5, -5]
print("PASS")
