import fernledger
from solution import statement_lines

ledger = fernledger.Ledger([("2026-06-01", "savings", 1234567.891), ("2026-06-02", "cash", 950.0),
                            ("2026-06-03", "cash", 120.5)])
assert statement_lines(ledger) == ["savings: 1,234,567.89", "cash: 1,070.50"]
print("PASS")
