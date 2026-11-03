from solution import account_balances

text = "date,account,amount\n2026-01-03,cash,120.50\n2026-01-09,bank,-40\n2026-02-01,cash,-20.25\n"
out = account_balances(text)
assert out == {"cash": 100.25, "bank": -40.0}
assert list(out) == ["cash", "bank"]
print("PASS")
