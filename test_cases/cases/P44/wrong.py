def fill_per_sensor(readings):
    """Fill each missing value with the last known value of the same sensor."""
    return readings.ffill()
