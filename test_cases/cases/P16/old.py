def has_mixed_labels(df):
    """Return True if the column labels of the table mix labels of different types."""
    return df.columns.is_mixed()
