import gridwell


def blur_tiles(heights):
    """Return the heights averaged over each cell and the eight cells around it, on a map whose edges
    wrap around, rounded to two decimal places."""
    return [[round(v, 2) for v in row] for row in gridwell.smooth(heights, radius=1, boundary="periodic")]
