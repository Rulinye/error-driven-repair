import gridwell


def brightest_after_clipping(image, ceiling):
    """Clip the image to the range [0, ceiling] and return the (row, column) of the brightest pixel;
    ties go to the first one in reading order."""
    return gridwell.peak_index(gridwell.clip(image, 0, ceiling))
