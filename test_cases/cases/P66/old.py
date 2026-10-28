import pandas as pd


def long_format(wide):
    """Reshape the table of home runs per year from wide to long format."""
    groups = {"year": ["year1", "year2"], "hr": ["hr1", "hr2"]}
    return pd.lreshape(wide, groups, label="obs")
