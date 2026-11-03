from collections import Counter

import pandas as pd


def most_common_sizes(sizes):
    """Return the most common size(s) of a Categorical of shirt sizes, as a list."""
    counts = Counter(size for size in sizes if pd.notna(size))
    top = max(counts.values(), default=0)
    return [size for size in sizes.categories if top > 0 and counts.get(size) == top]
