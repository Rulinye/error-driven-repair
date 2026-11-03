import pandas as pd


def with_total_row(report):
    """Return the report with a last row "total" that holds the sum of every column."""
    totals = report.sum()
    totals.name = "total"
    return pd.concat([report, totals.to_frame().T])
