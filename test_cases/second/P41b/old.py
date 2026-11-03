def shipment_summary(shipments):
    """Return the summary statistics of the shipping dates and the weights, with the dates treated as
    numbers (count, mean, minimum, quartiles, maximum)."""
    return shipments.describe(datetime_is_numeric=True)
