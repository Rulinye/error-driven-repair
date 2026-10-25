def column_max(df):
    return {col: s.max() for col, s in df.iteritems()}
