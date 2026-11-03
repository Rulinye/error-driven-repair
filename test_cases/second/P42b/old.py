def running_average(prices):
    """Return, at each step, the average of all prices up to that step."""
    return prices.expanding(min_periods=1, center=False).mean()
