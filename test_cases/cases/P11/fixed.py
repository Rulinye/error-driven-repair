def weekly_totals(sales):
    """Sum a daily sales Series (indexed by date) by week of the year."""
    return sales.groupby(sales.index.isocalendar().week).sum()
