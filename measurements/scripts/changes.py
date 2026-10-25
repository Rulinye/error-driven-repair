"""Load data/changes.csv, the list of the 100 candidate changes and the decision on each."""
import csv
import os

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "changes.csv")


def load_changes():
    """Return {change id: row}, where each row is a dict keyed by the CSV header."""
    with open(PATH, newline="", encoding="utf-8") as f:
        return {row["id"]: row for row in csv.DictReader(f)}


def is_planned(row):
    """One of the 86 planned changes: selected (75) or re-admitted after dropping the 'commonly used' criterion (11)."""
    return row["decision"] == "included" or row["reason"] == "rarely used"
