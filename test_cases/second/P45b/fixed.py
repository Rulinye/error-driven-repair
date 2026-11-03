def median_by_region(sales):
    """Return the median of the numeric columns per region."""
    return sales.groupby("region").median(numeric_only=True)
