def as_pairs(prices):
    """Return the prices as 'label=value' strings, in the order of the Series."""
    return [f"{label}={value:g}" for label, value in prices.iteritems()]
