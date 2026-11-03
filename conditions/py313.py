"""The original messages (E0) of the 90 test cases under Python 3.13 (Chapter 7).

usage: python conditions/py313.py
Run after `bash measurements/run_all.sh`, which builds the Python 3.13 environment (pandas 2.2.3, NumPy 2.1.3).

The study fixes Python 3.11. A project that is forced to upgrade typically moves to Python 3.13, the first Python
that requires pandas 2.2.3 and NumPy 2.1. For every test case, the program (old.py) is run with its test under
Python 3.13 as in conditions/error_variants.py, and the printed error is compared with E0 of
conditions/results/error_conditions.csv. Where Python 3.13 adds a suggestion for a keyword argument, the program is
run again with the argument renamed as suggested: the outcome is "correct fix" (the test passes), "wrong result"
(the program runs but the test's checks fail) or "fails" (it still raises an error).
Writes conditions/results/py313.csv.
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from error_variants import CASES, passes, printed_error, run_case  # noqa: E402

SUGGESTION = re.compile(r"Did you mean:? '?([^'?]+)'?\??\s*$")


def main():
    rows = []
    for r in csv.DictReader(open(os.path.join(HERE, "results", "error_conditions.csv"), encoding="utf-8")):
        cid = r["id"]
        old = open(os.path.join(CASES, cid, "old.py"), encoding="utf-8").read()
        e313 = printed_error(run_case("py313", cid, old))
        s311, s313 = SUGGESTION.search(r["E0"]), SUGGESTION.search(e313)
        follow = ""
        keyword = re.search(r"unexpected keyword argument '(\w+)'", e313)
        if s313 and not s311 and keyword:
            fixed = old.replace(keyword.group(1) + "=", s313.group(1) + "=")
            p = run_case("py313", cid, fixed)
            if passes(p):
                follow = "correct fix"
            elif "AssertionError" in p.stderr.strip().splitlines()[-1]:
                follow = "wrong result"
            else:
                follow = "fails"
        rows.append({"id": cid, "differs": e313 != r["E0"], "suggestion_311": s311.group(1) if s311 else "",
                     "suggestion_313": s313.group(1) if s313 else "", "follow_313_keyword_suggestion": follow,
                     "E0_311": r["E0"], "E0_313": e313})
    out = os.path.join(HERE, "results", "py313.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    diff = [x for x in rows if x["differs"]]
    print(f"{len(rows)} test cases; E0 differs between Python 3.11 and 3.13 for {len(diff)}")
    for x in diff:
        change = ("adds the suggestion '" + x["suggestion_313"] + "'" if x["suggestion_313"] and not x["suggestion_311"]
                  else "loses the suggestion '" + x["suggestion_311"] + "'" if x["suggestion_311"] and not x["suggestion_313"]
                  else "suggestion '" + x["suggestion_311"] + "' -> '" + x["suggestion_313"] + "'" if x["suggestion_311"]
                  else "other difference")
        print(f"  {x['id']}: {change}" + (f"; following it: {x['follow_313_keyword_suggestion']}"
                                          if x["follow_313_keyword_suggestion"] else ""))
        if change == "other difference":
            print(f"      3.11: {x['E0_311'][-150:]}\n      3.13: {x['E0_313'][-150:]}")


if __name__ == "__main__":
    main()
