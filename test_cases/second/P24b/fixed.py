def unsigned_order_numbers(orders):
    """Return a copy of the order numbers (the row labels of the table) as unsigned 64-bit integers."""
    return orders.index.copy().astype("uint64")
