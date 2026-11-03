# fernledger 2.0.0 (October 2026)

## Removals and renamed functions

- Removed `parse_entries`; read a ledger from text with `read_journal` instead, which takes the same arguments (#412).
- `merge` has been removed. Use `chain`, which joins any number of ledgers in the order given (#398).
- Removed `Ledger.tally`; use `Ledger.bucketize` with the same `by` argument (#405).
- The `start` argument of `Ledger.running_total` has been removed; pass the opening balance as `opening` (#421).
- The `thousands` argument of `fmt_amount` has been removed; use `style="grouped"` to add thousands separators (#430).

## Other changes

- `Ledger.balance` now accepts a list of accounts and returns their combined balance (#377).
- `monthly_totals` now returns the months in calendar order instead of the order in which they first occur (#389).
- `parse_date` now also accepts dates written as YYYY/MM/DD (#402).
