import pandas as pd


def most_common_sizes(sizes):
    """Return the most common size(s) of a Categorical of shirt sizes, as a list."""
    return list(pd.Series(sizes).mode())
