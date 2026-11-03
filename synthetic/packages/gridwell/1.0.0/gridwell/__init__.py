"""gridwell: small numeric grids stored as lists of rows."""

__version__ = "1.0.0"

_REMOVED = {
    "row_means": "gridwell.collapse(g, 'mean', axis=1)",
    "peak_index": "gridwell.locate(g, 'max')",
}


def __getattr__(name):
    if name in _REMOVED:
        raise AttributeError(f"`gridwell.{name}` was removed in gridwell 1.0. Use `{_REMOVED[name]}` instead.")
    raise AttributeError(f"module 'gridwell' has no attribute '{name}'")


def _check(g):
    rows = [list(r) for r in g]
    if not rows or any(len(r) != len(rows[0]) for r in rows):
        raise ValueError("a grid needs at least one row and rows of equal length")
    return rows


def shape(g):
    """(number of rows, number of columns)."""
    rows = _check(g)
    return len(rows), len(rows[0])


def zeros(rows, cols):
    """A grid of zeros."""
    return [[0] * cols for _ in range(rows)]


def full(rows, cols, value):
    """A grid filled with one value."""
    return [[value] * cols for _ in range(rows)]


def row_sums(g):
    """The sum of each row."""
    return [sum(r) for r in _check(g)]


def col_sums(g):
    """The sum of each column."""
    rows = _check(g)
    return [sum(r[c] for r in rows) for c in range(len(rows[0]))]


def collapse(g, how="sum", axis=0):
    """Reduce the grid along one axis: how is "sum", "mean", "max" or "min"; axis=0 gives one value per
    column, axis=1 one value per row."""
    rows = _check(g)
    reduce = {"sum": sum, "mean": lambda v: sum(v) / len(v), "max": max, "min": min}
    if how not in reduce:
        raise ValueError("how must be 'sum', 'mean', 'max' or 'min'")
    if axis == 0:
        return [reduce[how]([r[c] for r in rows]) for c in range(len(rows[0]))]
    if axis == 1:
        return [reduce[how](r) for r in rows]
    raise ValueError("axis must be 0 or 1")


def locate(g, which="max"):
    """(row, column) of the largest (which="max") or smallest (which="min") value; the first one in
    row-major order if it occurs more than once."""
    rows = _check(g)
    if which not in ("max", "min"):
        raise ValueError("which must be 'max' or 'min'")
    better = (lambda v, w: v > w) if which == "max" else (lambda v, w: v < w)
    best = None
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            if best is None or better(v, rows[best[0]][best[1]]):
                best = (i, j)
    return best


def clip(g, low, high):
    """Each value limited to the range [low, high]."""
    if low > high:
        raise ValueError("low must not be greater than high")
    return [[min(max(v, low), high) for v in r] for r in _check(g)]


def rotate(g, turns=1):
    """The grid turned clockwise by 90 degrees, turns times; negative turns go counterclockwise."""
    if not isinstance(turns, int):
        raise TypeError("turns must be an integer")
    rows = _check(g)
    for _ in range(turns % 4):
        rows = [list(r) for r in zip(*rows[::-1])]
    return rows


def stack(a, b, axis=0):
    """Two grids joined downwards (axis=0) or side by side (axis=1)."""
    ra, rb = _check(a), _check(b)
    if axis == 0:
        if len(ra[0]) != len(rb[0]):
            raise ValueError("grids must have the same number of columns")
        return ra + rb
    if len(ra) != len(rb):
        raise ValueError("grids must have the same number of rows")
    return [x + y for x, y in zip(ra, rb)]


def tile(g, layout=(1, 1)):
    """The grid repeated layout[0] times downwards and layout[1] times to the right."""
    rows = _check(g)
    down, right = layout
    return [list(r) * right for _ in range(down) for r in rows]


def smooth(g, radius=1, boundary="clip"):
    """The mean of each cell and its neighbors within radius. boundary="periodic" treats the grid as
    periodic; boundary="clip" averages only the cells inside the grid."""
    if boundary not in ("clip", "periodic"):
        raise ValueError("boundary must be 'clip' or 'periodic'")
    rows = _check(g)
    n, m = len(rows), len(rows[0])
    out = []
    for i in range(n):
        line = []
        for j in range(m):
            vals = []
            for di in range(-radius, radius + 1):
                for dj in range(-radius, radius + 1):
                    a, b = i + di, j + dj
                    if boundary == "periodic":
                        vals.append(rows[a % n][b % m])
                    elif 0 <= a < n and 0 <= b < m:
                        vals.append(rows[a][b])
            line.append(sum(vals) / len(vals))
        out.append(line)
    return out


class Grid:
    """A grid with cell access by (row, column)."""

    def __init__(self, rows):
        self._rows = _check(rows)

    @property
    def shape(self):
        return len(self._rows), len(self._rows[0])

    def cell(self, r, c):
        return self._rows[r][c]

    def rows(self):
        return [list(r) for r in self._rows]

    def map(self, fn):
        """A new grid with fn applied to every value."""
        return Grid([[fn(v) for v in r] for r in self._rows])

    def ring(self, r, c, radius=1):
        """The values around cell (r, c) within radius, in row-major order, without the cell itself;
        cells outside the grid are left out."""
        n, m = self.shape
        out = []
        for a in range(r - radius, r + radius + 1):
            for b in range(c - radius, c + radius + 1):
                if (a, b) != (r, c) and 0 <= a < n and 0 <= b < m:
                    out.append(self._rows[a][b])
        return out
