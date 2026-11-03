def rename_columns(df, names):
    """Return the table with the given column names."""
    df.columns = names
    return df
