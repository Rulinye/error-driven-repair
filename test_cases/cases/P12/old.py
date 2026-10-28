def add_week(visits):
    """Return a copy of the visits with a column week: the week of the year of the visit date."""
    out = visits.copy()
    out["week"] = out["date"].dt.week
    return out
