import contextlib
import io


def summary_text(df):
    """Return the info summary of the table, including the number of non-null values per column."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        df.info(show_counts=True)
    return buf.getvalue()
