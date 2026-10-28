import pandas as pd
from solution import to_windows_csv

out = to_windows_csv(pd.DataFrame({"a": [1, 2], "b": ["x", "y"]}))
assert out == "a,b\r\n1,x\r\n2,y\r\n"
print("PASS")
