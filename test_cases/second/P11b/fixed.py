def add_week_column(visits):
    """Return a copy of the table of visits (indexed by date) with a column "week": the week of the year."""
    out = visits.copy()
    out["week"] = out.index.isocalendar().week
    return out
