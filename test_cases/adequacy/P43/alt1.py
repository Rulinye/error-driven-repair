def nearest_position(index, value):
    """Return the position of the label nearest to the value in a sorted numeric index."""
    return index.get_indexer([value], method="nearest").item()
