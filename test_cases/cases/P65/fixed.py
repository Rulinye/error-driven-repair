def sem_per_group(values):
    """Return the standard error of the mean of the values of each group (the index level "group")."""
    return values.groupby(level="group").sem()
