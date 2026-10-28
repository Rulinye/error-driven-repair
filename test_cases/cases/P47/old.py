import pandas as pd


def parse_signup_dates(texts):
    """Parse sign-up dates typed in by users; some are day-month-year, some year-month-day."""
    return pd.to_datetime(texts)
