import pandas as pd
from solution import non_missing_counts

table = pd.DataFrame({"age": [31, None, 45], "city": ["a", "b", None], "score": [1.0, 2.0, 3.0]})
out = non_missing_counts(table)
assert out == {"age": 2, "city": 2, "score": 3}
assert list(out) == ["age", "city", "score"]
print("PASS")
