import math
from solution import nearest_distance

assert nearest_distance([3, 10], 4) == 1
empty = nearest_distance([], 4)
assert math.isinf(empty) and empty > 0
print("PASS")
