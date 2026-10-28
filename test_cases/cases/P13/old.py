def plain_values(grades):
    """Return the values of a Categorical of grades as a plain NumPy array."""
    return grades.to_dense()
