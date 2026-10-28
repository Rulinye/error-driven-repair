import pandas as pd


def price_levels(prices):
    """Return a float index named price built from the given prices."""
    return pd.Index(prices, name="price")
