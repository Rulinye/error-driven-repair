import fernledger
from solution import combined_balance

first = fernledger.Ledger([("2026-07-01", "cash", 40.0), ("2026-07-02", "bank", 10.0)])
second = fernledger.Ledger([("2026-07-05", "cash", -15.5), ("2026-07-06", "cash", 2.25)])
assert combined_balance(first, second, "cash") == 26.75
assert combined_balance(first, second, "bank") == 10.0
assert len(first) == 2 and len(second) == 2
print("PASS")
