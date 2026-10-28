def all_trading_days(first, others):
    """Return, sorted, every day that is in the DatetimeIndex of trading days or in one of the other indexes."""
    return first.union_many(others)
