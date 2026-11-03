"""gridwell: small numeric grids stored as lists of rows."""

__version__ = "0.9.4"


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


def row_means(g):
    """The mean of each row."""
    return [sum(r) / len(r) for r in _check(g)]


def peak_index(g):
    """(row, column) of the largest value; the first one in row-major order if it occurs more than once."""
    rows = _check(g)
    best = None
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            if best is None or v > rows[best[0]][best[1]]:
                best = (i, j)
    return best


def clip(g, low, high):
    """Each value limited to the range [low, high]."""
    return [[min(max(v, low), high) for v in r] for r in _check(g)]


def rotate(g, turns=1):
    """The grid turned clockwise by 90 degrees, turns times (0 to 3)."""
    rows = _check(g)
    for _ in range(turns % 4):
        rows = [list(r) for r in zip(*rows[::-1])]
    return rows


def tile(g, reps=(1, 1)):
    """The grid repeated reps[0] times downwards and reps[1] times to the right."""
    rows = _check(g)
    down, right = reps
    return [list(r) * right for _ in range(down) for r in rows]


def smooth(g, radius=1, wrap=False):
    """The mean of each cell and its neighbors within radius; with wrap=True, the grid is periodic,
    otherwise only cells inside the grid are averaged."""
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
                    if wrap:
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

    def neighbors(self, r, c, radius=1):
        """The values around cell (r, c) within radius, in row-major order, without the cell itself;
        cells outside the grid are left out."""
        n, m = self.shape
        out = []
        for a in range(r - radius, r + radius + 1):
            for b in range(c - radius, c + radius + 1):
                if (a, b) != (r, c) and 0 <= a < n and 0 <= b < m:
                    out.append(self._rows[a][b])
        return out
