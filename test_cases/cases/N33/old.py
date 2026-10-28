def swap_byte_order(arr):
    """Return a view of the array whose dtype has the opposite byte order; the bytes stay as they are."""
    return arr.newbyteorder()
