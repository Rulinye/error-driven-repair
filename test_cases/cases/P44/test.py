import math
import pandas as pd
from solution import fill_per_sensor

readings = pd.DataFrame({"sensor": ["a", "a", "b", "b", "a"], "value": [1.0, None, None, 2.0, None]})
out = fill_per_sensor(readings)
values = out["value"].tolist()
assert values[:2] == [1.0, 1.0] and math.isnan(values[2]) and values[3:] == [2.0, 1.0]
print("PASS")
