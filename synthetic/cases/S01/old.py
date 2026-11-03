import fernledger


def account_balances(csv_text):
    """Return the balance of every account in a journal of 'date,account,amount' lines with a header."""
    ledger = fernledger.parse_entries(csv_text, skip_header=True)
    return {account: ledger.balance(account) for account in ledger.accounts()}
