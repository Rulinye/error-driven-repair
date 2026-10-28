import pandas as pd


def single_label(label):
    """Return a Categorical that holds just the given label."""
    return pd.Categorical(label)
