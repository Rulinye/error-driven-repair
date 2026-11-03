def column_spread(df):
    """Return the mean absolute deviation of each column around its mean."""
    return df.apply(lambda col: (col - col.mean()).abs().mean())
