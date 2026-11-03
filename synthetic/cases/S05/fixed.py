import fernledger


def combined_balance(first, second, account):
    """Return the balance of the account over two ledgers taken together."""
    return fernledger.chain(first, second).balance(account)
