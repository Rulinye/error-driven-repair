def with_datetime_column(df, column):
    """Return a copy of the table in which the given column has a datetime dtype."""
    out = df.copy()
    out[column] = out[column].astype("datetime64[D]")
    return out
