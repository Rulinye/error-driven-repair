import numpy as np
from solution import as_matrix

m = as_matrix([[1, 2], [3, 4]])
assert isinstance(m, np.matrix)
assert (m * m).tolist() == [[7, 10], [15, 22]]
print("PASS")
