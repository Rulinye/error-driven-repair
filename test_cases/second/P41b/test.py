import pandas as pd
from solution import shipment_summary

shipments = pd.DataFrame({"shipped": pd.to_datetime(["2024-02-01", "2024-02-03", "2024-02-08"]),
                          "weight": [2.0, 4.0, 9.0]})
out = shipment_summary(shipments)
assert out.loc["count", "shipped"] == 3
assert out.loc["mean", "shipped"] == pd.Timestamp("2024-02-04")
assert out.loc["max", "shipped"] == pd.Timestamp("2024-02-08")
assert out.loc["mean", "weight"] == 5.0
print("PASS")
