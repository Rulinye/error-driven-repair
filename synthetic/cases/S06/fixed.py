import gridwell


def row_averages(readings):
    """Return the average reading of each row, rounded to one decimal place."""
    return [round(m, 1) for m in gridwell.collapse(readings, "mean", axis=1)]
