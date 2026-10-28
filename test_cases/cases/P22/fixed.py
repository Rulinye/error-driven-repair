def to_windows_csv(df):
    """Return the table as CSV text with Windows line endings (CR LF)."""
    return df.to_csv(index=False, lineterminator="\r\n")
