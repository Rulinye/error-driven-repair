def balance_history(ledger, account, carried_over):
    """Return the balance of the account after each of its entries, starting from the amount carried over."""
    return ledger.running_total(account, start=carried_over)
