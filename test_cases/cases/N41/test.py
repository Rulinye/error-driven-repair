import numpy as np
from solution import joint_density

hist, xedges, yedges = joint_density([0, 0, 0, 2], [0, 0, 2, 2], 2)
assert np.allclose(hist, [[0.5, 0.25], [0.0, 0.25]])
assert xedges.tolist() == [0.0, 1.0, 2.0]
print("PASS")
