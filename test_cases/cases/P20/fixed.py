import io


def summary_text(df):
    """Return the info summary of the table, including the number of non-null values per column."""
    buf = io.StringIO()
    df.info(buf=buf, show_counts=True)
    return buf.getvalue()
