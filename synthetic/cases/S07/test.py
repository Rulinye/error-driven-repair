from solution import local_maxima

rows = [[1, 2, 1, 0],
        [2, 5, 2, 1],
        [1, 2, 1, 7],
        [0, 1, 3, 2]]
assert local_maxima(rows) == [(1, 1), (2, 3)]
print("PASS")
