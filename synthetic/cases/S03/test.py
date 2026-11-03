import fernledger
from solution import balance_history

ledger = fernledger.Ledger([("2026-05-01", "cash", 12.5), ("2026-05-02", "bank", 50.0),
                            ("2026-05-04", "cash", -7.25), ("2026-05-09", "cash", 3.0)])
assert balance_history(ledger, "cash", 100) == [112.5, 105.25, 108.25]
assert balance_history(ledger, "bank", 0) == [50.0]
print("PASS")
