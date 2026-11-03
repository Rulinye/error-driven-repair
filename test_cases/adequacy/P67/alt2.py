def index_by_id(df):
    """Use the id column as the index and keep it as a column as well."""
    out = df.copy()
    out.index = out["id"]
    return out
