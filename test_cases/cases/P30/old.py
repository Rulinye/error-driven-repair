def total_by_region(sales):
    """Sum a Series of sales indexed by (region, city) over the cities of each region."""
    return sales.sum(level="region")
