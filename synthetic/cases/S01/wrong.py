import fernledger


def account_balances(csv_text):
    """Return the balance of every account in a journal of 'date,account,amount' lines with a header."""
    ledger = fernledger.Ledger(line.split(",") for line in csv_text.splitlines() if line.strip())
    return {account: ledger.balance(account) for account in ledger.accounts()}
