def swap_byte_order(arr):
    """Return a view of the array whose dtype has the opposite byte order; the bytes stay as they are."""
    out = arr.view()
    out.dtype = arr.dtype.newbyteorder()
    return out
