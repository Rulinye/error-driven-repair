import pandas as pd
from solution import read_ids

out = read_ids("id,name\n7,ann\n9,bob\n")
assert isinstance(out, pd.Series)
assert out.name == "id" and out.tolist() == [7, 9] and out.dtype == "int64"
one = read_ids("id,name\n3,cy\n")
assert isinstance(one, pd.Series) and one.tolist() == [3]
print("PASS")
