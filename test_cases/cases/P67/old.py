def index_by_id(df):
    """Use the id column as the index and keep it as a column as well."""
    return df.set_index("id", False)
