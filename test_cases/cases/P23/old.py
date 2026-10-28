def rename_columns(df, names):
    """Return the table with the given column names."""
    df.set_axis(names, axis=1, inplace=True)
    return df
