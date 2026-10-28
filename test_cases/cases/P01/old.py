def add_order(orders, order):
    """Return the table of orders with one more order (a dict) at the end."""
    return orders.append(order, ignore_index=True)
