import pandas as pd
from solution import parse_due_dates

invoices = pd.DataFrame({"due": ["31/01/2024", "2024-02-15", "15/03/2024"]})
out = parse_due_dates(invoices)
assert [d.strftime("%Y-%m-%d") for d in out] == ["2024-01-31", "2024-02-15", "2024-03-15"]
print("PASS")
