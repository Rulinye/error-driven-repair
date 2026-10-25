def mean_by_team(df):
    return df.groupby("team").mean()
