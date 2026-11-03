# gridwell 1.0.0 (September 2026)

## Removed and changed functions

- `gridwell.row_means` was removed. Use `gridwell.collapse(g, "mean", axis=1)`, which reduces a grid along either axis with sum, mean, max or min (gh-212).
- `gridwell.peak_index` was removed in favor of `gridwell.locate(g, "max")`, which can also find the smallest value (gh-219).
- `Grid.neighbors` was renamed to `Grid.ring` (gh-230).
- The `wrap` keyword of `smooth` was removed. Pass `boundary="periodic"` for a periodic grid; the default, `boundary="clip"`, keeps the previous behavior (gh-241).
- The `reps` keyword of `tile` was replaced by `layout` (gh-244).

## Other changes

- New function `gridwell.stack` joins two grids downwards or side by side (gh-201).
- `rotate` raises a TypeError if `turns` is not an integer; negative values turn the grid counterclockwise (gh-226).
- `clip` raises a ValueError if `low` is greater than `high` (gh-235).
