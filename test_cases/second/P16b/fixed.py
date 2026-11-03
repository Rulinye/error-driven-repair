def labels_need_cleaning(series):
    """Return True if the labels of the Series mix text with non-integer numbers."""
    return series.index.inferred_type == "mixed"
