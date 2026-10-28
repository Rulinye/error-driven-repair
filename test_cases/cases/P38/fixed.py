def with_levels(ratings, levels):
    """Return the Categorical of ratings with the given categories, in the given order."""
    ratings = ratings.set_categories(levels)
    return ratings
