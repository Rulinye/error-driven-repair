def labels_as_text(index):
    """Return the labels of an index as strings, for writing to a text report."""
    return list(index.to_native_types())
