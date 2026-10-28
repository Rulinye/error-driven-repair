def total_per_store(sales):
    """Return the total amount of sales per store."""
    return sales.groupby("store", squeeze=True)["amount"].sum()
