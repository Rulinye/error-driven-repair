def shifted_level(level, offset):
    """Add the offset to an 8-bit level (a NumPy uint8) and return the sum as an integer."""
    return int(level + offset)
