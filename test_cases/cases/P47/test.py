from solution import parse_signup_dates

out = parse_signup_dates(["13-01-2000", "2000-01-12", "25-12-1999"])
assert [d.strftime("%Y-%m-%d") for d in out] == ["2000-01-13", "2000-01-12", "1999-12-25"]
print("PASS")
