"""Test adequacy (Section 3.2.4): do the tests accept other correct fixes?

usage: python test_cases/check_adequacy.py
Run from the repository root after `bash measurements/run_all.sh` has built the environments.

For 18 test cases drawn at random (random.Random(20261105).sample over the 90 test cases, in the order of
runs/prompts.py), adequacy/<id>/ holds two or three correct fixes that differ from the reference fix, and
adequacy/list.csv says how each one differs. A fix is correct if it gives the result of the old version in
general, not only on the test input. Each one is run with the test in the new environment (as in
check_cases.py) and checked with the static validity checks; it is accepted if it passes both.
Writes test_cases/results/adequacy.csv.
"""
import csv
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
from check_cases import CASES, run  # noqa: E402
from validity import check  # noqa: E402

ADEQUACY = os.path.join(HERE, "adequacy")


def main():
    envs = os.path.abspath(os.path.join(ROOT, "measurements", "envs"))
    new = {"pandas": os.path.join(envs, "mid", "bin", "python"), "numpy": os.path.join(envs, "new", "bin", "python")}
    library = {r["id"]: r["library"] for r in csv.DictReader(open(os.path.join(HERE, "list.csv"), encoding="utf-8"))}
    alternatives = list(csv.DictReader(open(os.path.join(ADEQUACY, "list.csv"), encoding="utf-8")))
    rows = []
    for a in alternatives:
        cid, name = a["id"], a["file"]
        case_dir = os.path.join(CASES, cid)
        code = open(os.path.join(ADEQUACY, cid, name), encoding="utf-8").read()
        old = open(os.path.join(case_dir, "old.py"), encoding="utf-8").read()
        with tempfile.TemporaryDirectory() as tmp:  # run() takes the candidate and test.py from one folder
            shutil.copy(os.path.join(case_dir, "test.py"), os.path.join(tmp, "test.py"))
            shutil.copy(os.path.join(ADEQUACY, cid, name), os.path.join(tmp, name))
            passed, error, _ = run(new[library[cid].lower()], tmp, name)
        violations = check(code, old)
        rows.append({"id": cid, "library": library[cid], "file": name, "alternative": a["alternative"],
                     "passes_test": passed, "validity": "; ".join(violations) or "valid",
                     "accepted": passed and not violations, "error": "" if passed else error})
        print(f"{'ok ' if rows[-1]['accepted'] else '-- '}{cid} {name}  test={passed!s:5} "
              f"validity={rows[-1]['validity']}  | {a['alternative']}")
    out = os.path.join(HERE, "results", "adequacy.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    cases = sorted({r["id"] for r in rows}, key=lambda c: (c[0] == "N", c))
    print(f"accepted {sum(r['accepted'] for r in rows)} of {len(rows)} alternative fixes "
          f"on {len(cases)} test cases -> {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
