import pandas as pd


def customer_index(ids):
    """Return an integer index named customer_id built from the given ids."""
    return pd.Int64Index(ids, name="customer_id")
