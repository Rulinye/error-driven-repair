def rename_columns(df, names):
    """Return the table with the given column names."""
    return df.set_axis(names, axis="columns")
