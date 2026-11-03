import gridwell


def local_maxima(rows):
    """Return the (row, column) positions whose value is larger than all of the values around them."""
    grid = gridwell.Grid(rows)
    n, m = grid.shape
    return [(r, c) for r in range(n) for c in range(m)
            if all(grid.cell(r, c) > v for v in grid.neighbors(r, c))]
