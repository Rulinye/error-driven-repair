import pandas as pd


def parse_due_dates(invoices):
    """Return the due dates of the invoices as datetimes; clerks typed some as day/month/year and some as
    year-month-day."""
    return pd.to_datetime(invoices["due"])
