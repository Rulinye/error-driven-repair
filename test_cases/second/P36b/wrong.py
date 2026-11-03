def lunch_orders(orders):
    """Return the orders placed from 11:30 up to, but not including, 14:00."""
    return orders.between_time("11:30", "14:00")
