def with_levels(ratings, levels):
    """Return the Categorical of ratings with the given categories, in the given order."""
    ratings.set_categories(levels, inplace=True)
    return ratings
