def column_spread(df):
    """Return the mean absolute deviation of each column around its mean."""
    return (df - df.median()).abs().median()
