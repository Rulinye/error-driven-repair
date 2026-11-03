def non_missing_counts(table):
    """Return a dict that maps each column name to the number of values in it that are not missing."""
    return {name: int(column.notna().sum()) for name, column in table.iterrows()}
