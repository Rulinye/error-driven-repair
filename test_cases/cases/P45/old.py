def mean_by_team(df):
    """Average the numeric columns of the table per team."""
    return df.groupby("team").mean()
