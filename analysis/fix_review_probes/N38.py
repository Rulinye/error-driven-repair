# Ragged and regular rows of several shapes; are warnings left over?
import warnings

import numpy as np
from solution import is_ragged

for rows in ([[1, 2], [3]], [[1, 2], [3, 4]], [1, [2, 3]], [], [[1], [2]], [[[1, 2]], [[3]]], np.array([[1, 2]]),
             [(1, 2), (3,)], ["ab", "c"]):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            result = is_ragged(rows)
        except Exception as e:
            result = type(e).__name__
    print(repr(rows), result, f"warnings: {len(caught)}")
