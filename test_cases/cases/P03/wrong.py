def column_ranges(df):
    """Return a dict that maps each numeric column to its maximum minus its minimum."""
    ranges = {}
    for name, column in df.iterrows():
        if column.dtype.kind in "if":
            ranges[name] = column.max() - column.min()
    return ranges
