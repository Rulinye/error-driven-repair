"""fernledger: ledgers of dated amounts on named accounts."""

__version__ = "1.6.0"


def parse_date(text):
    """Check a date written as YYYY-MM-DD and return it as a (year, month, day) tuple."""
    parts = str(text).strip().split("-")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise ValueError(f"not a date: {text!r}")
    year, month, day = (int(p) for p in parts)
    if not (1 <= month <= 12 and 1 <= day <= 31):
        raise ValueError(f"not a date: {text!r}")
    return year, month, day


def month_key(date):
    """The month of a date, as YYYY-MM."""
    year, month, _ = parse_date(date)
    return f"{year:04d}-{month:02d}"


class Ledger:
    """An ordered list of (date, account, amount) entries."""

    def __init__(self, entries=()):
        self._entries = []
        for date, account, amount in entries:
            parse_date(date)
            self._entries.append((str(date).strip(), str(account), float(amount)))

    def __len__(self):
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)

    def __repr__(self):
        return f"Ledger({len(self._entries)} entries)"

    def accounts(self):
        """The accounts, in the order in which they first appear."""
        seen = []
        for _, account, _ in self._entries:
            if account not in seen:
                seen.append(account)
        return seen

    def entries_for(self, account):
        """The entries of one account."""
        return [e for e in self._entries if e[1] == account]

    def balance(self, account=None):
        """The sum of the amounts of one account, or of all accounts."""
        return round(sum(x for _, a, x in self._entries if account is None or a == account), 2)

    def total(self):
        """The sum of all amounts."""
        return self.balance()

    def filter(self, predicate):
        """A new ledger with the entries for which predicate(entry) is true."""
        return Ledger(e for e in self._entries if predicate(e))

    def running_total(self, account, start=0.0):
        """The balance of one account after each of its entries, beginning at start."""
        out, value = [], float(start)
        for _, _, amount in self.entries_for(account):
            value += amount
            out.append(round(value, 2))
        return out

    def tally(self, by="account"):
        """Sums of the amounts per account (by="account") or per month (by="month")."""
        if by not in ("account", "month"):
            raise ValueError("by must be 'account' or 'month'")
        sums = {}
        for date, account, amount in self._entries:
            key = account if by == "account" else month_key(date)
            sums[key] = round(sums.get(key, 0.0) + amount, 2)
        return sums

    def to_rows(self):
        """The entries as dictionaries."""
        return [{"date": d, "account": a, "amount": x} for d, a, x in self._entries]


def parse_entries(text, sep=",", skip_header=False):
    """Read a ledger from text with one 'date,account,amount' entry per line."""
    lines = [line for line in str(text).splitlines() if line.strip()]
    if skip_header:
        lines = lines[1:]
    entries = []
    for line in lines:
        date, account, amount = (part.strip() for part in line.split(sep))
        entries.append((date, account, amount))
    return Ledger(entries)


def merge(first, second):
    """A ledger with the entries of the first ledger followed by those of the second."""
    return Ledger(list(first) + list(second))


def monthly_totals(ledger, account=None):
    """Sums of the amounts per month, for one account or all accounts."""
    sums = {}
    for date, a, amount in ledger:
        if account is None or a == account:
            key = month_key(date)
            sums[key] = round(sums.get(key, 0.0) + amount, 2)
    return sums


def fmt_amount(x, places=2, thousands=False):
    """Format an amount with a fixed number of decimal places, optionally with thousands separators."""
    spec = f",.{int(places)}f" if thousands else f".{int(places)}f"
    return format(float(x), spec)
