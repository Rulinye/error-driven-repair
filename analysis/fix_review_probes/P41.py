# Is the input table changed? Also missing values with a time zone, and a slice of a table.
import pandas as pd
from solution import date_summary

events = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-01-03", "2024-01-08"]), "x": [1, 2, 3]})
before = events.copy()
print(date_summary(events).to_dict(), "| input unchanged:", events.equals(before))
utc = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", None, "2024-01-08"]).tz_localize("UTC")})
print(date_summary(utc).to_dict())
table = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-01-03"]), "x": [1, 2]})
print(date_summary(table[table["x"] > 0]).to_dict())
