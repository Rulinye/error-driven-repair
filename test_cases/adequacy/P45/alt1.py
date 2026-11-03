def mean_by_team(df):
    """Average the numeric columns of the table per team."""
    values = df.drop(columns="team").select_dtypes(include=["number", "bool"])
    return values.groupby(df["team"]).mean()
