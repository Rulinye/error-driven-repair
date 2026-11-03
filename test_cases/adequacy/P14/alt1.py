import pandas as pd


def most_common_sizes(sizes):
    """Return the most common size(s) of a Categorical of shirt sizes, as a list."""
    counts = pd.Series(sizes).value_counts(sort=False)
    top = counts.max() if len(counts) else 0
    return [size for size, n in counts.items() if n == top and n > 0]
