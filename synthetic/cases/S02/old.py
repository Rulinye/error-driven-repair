def spending_by_month(ledger):
    """Return the total of the negative amounts per month, as positive numbers."""
    outgoing = ledger.filter(lambda entry: entry[2] < 0)
    return {month: -total for month, total in outgoing.tally(by="month").items()}
