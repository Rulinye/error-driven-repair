def mean_by_team(df):
    """Average the numeric columns of the table per team."""
    return df.groupby("team").agg("mean", numeric_only=True)
