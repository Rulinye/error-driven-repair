import pandas as pd


def add_order(orders, order):
    """Return the table of orders with one more order (a dict) at the end."""
    return pd.concat([orders, pd.DataFrame([order])], ignore_index=True)
