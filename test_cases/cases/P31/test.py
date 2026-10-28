import pandas as pd
from solution import read_column

out = read_column("price\n1.5\n2.0\n")
assert isinstance(out, pd.Series)
assert out.name == "price" and out.tolist() == [1.5, 2.0] and out.dtype == "float64"
one = read_column("price\n1.5\n")
assert isinstance(one, pd.Series) and one.tolist() == [1.5]
print("PASS")
