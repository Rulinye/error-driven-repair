import pandas as pd
from solution import nearest_position

index = pd.Index([10, 20, 30])
assert nearest_position(index, 22) == 1
assert nearest_position(index, 26) == 2
assert nearest_position(index, 20) == 1
print("PASS")
