def stores_with_returns(returns):
    """For each store (the first index level), tell whether any of its days had returns in each category."""
    return (returns > 0).any(axis=0)
