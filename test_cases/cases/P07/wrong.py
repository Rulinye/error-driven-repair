import pandas as pd


def checksum_index(checksums):
    """Return an unsigned 64-bit index built from the given checksums."""
    return pd.Index(checksums)
