import fernledger
from solution import spending_by_month

ledger = fernledger.Ledger([("2026-03-02", "cash", -12.5), ("2026-03-15", "bank", 900.0),
                            ("2026-03-20", "bank", -30.0), ("2026-04-01", "cash", -7.25)])
out = spending_by_month(ledger)
assert out == {"2026-03": 42.5, "2026-04": 7.25}
print("PASS")
