import fernledger


def statement_lines(ledger):
    """Return one line per account with its balance, formatted with thousands separators."""
    return [f"{account}: {fernledger.fmt_amount(ledger.balance(account), thousands=True)}"
            for account in ledger.accounts()]
