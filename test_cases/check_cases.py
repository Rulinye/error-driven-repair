"""Admission checks for the test cases (Sections 3.2.3, 3.2.4 and 3.9).

usage: python test_cases/check_cases.py [IDS ...]
Run from the repository root after `bash measurements/run_all.sh` has built the environments.
Checks every folder in test_cases/cases/ (or only the given ids) and writes test_cases/results/checks.csv.

Each folder holds old.py (the program with the old API), test.py (imports the program as `solution` and
prints PASS), fixed.py (the reference fix), meta.json, and, where a plausible wrong fix exists, wrong.py.

Execution checks (pandas: old = pandas 1.5.3 + NumPy 1.23.5, new = pandas 2.2.3 + NumPy 1.23.5;
NumPy: old = pandas 2.2.3 + NumPy 1.23.5, new = pandas 2.2.3 + NumPy 2.1.3), each within 60 seconds:
  1. old.py passes the test in the old environment;
  2. old.py fails in the new environment with an exception other than AssertionError;
  3. fixed.py passes in the new environment;
  4. wrong.py, if present, fails the test in the new environment or fails the validity checks.
Leakage: old.py must not contain the fix as the knowledge probe matches it (probe/questions.py); the
12 test cases whose fix is not a name are reviewed by hand.
Validity: fixed.py passes the static checks of test_cases/validity.py.

The error that old.py raises in the new environment, and the line of old.py that raises it, are
recorded for the error and documentation conditions.
"""
import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
CASES = os.path.join(HERE, "cases")
sys.path.insert(0, os.path.join(ROOT, "probe"))
sys.path.insert(0, HERE)
from questions import REVIEW, matches  # noqa: E402
from validity import check  # noqa: E402

TIMEOUT = 60
HEADER = re.compile(r"^[A-Za-z_][\w.]*(Error|Exception|Warning|Interrupt|Exit)\b")
FRAME = re.compile(r'^\s*File ".*[/\\]solution\.py", line (\d+)')


def run(python, case_dir, candidate):
    """Run the test on one program; return (passed, error text, line number in the program)."""
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(os.path.join(case_dir, candidate), os.path.join(tmp, "solution.py"))
        shutil.copy(os.path.join(case_dir, "test.py"), os.path.join(tmp, "test.py"))
        try:
            p = subprocess.run([python, "-W", "ignore", "test.py"], cwd=tmp, capture_output=True, text=True,
                               timeout=TIMEOUT, check=False)
        except subprocess.TimeoutExpired:
            return False, "timeout", None
    passed = p.returncode == 0 and p.stdout.strip().endswith("PASS")
    lines = p.stderr.rstrip().splitlines()
    starts = [i for i, line in enumerate(lines) if HEADER.match(line)]
    error = "\n".join(lines[starts[-1]:]) if starts else "\n".join(lines[-1:])
    numbers = [int(m.group(1)) for line in lines if (m := FRAME.match(line))]
    return passed, error, numbers[-1] if numbers else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--envs", default=os.path.join(ROOT, "measurements", "envs"))
    a = ap.parse_args()
    py = {e: os.path.join(os.path.abspath(a.envs), e, "bin", "python") for e in ("old", "mid", "new")}
    envs = {"pandas": (py["old"], py["mid"]), "numpy": (py["mid"], py["new"])}
    cases = {r["id"]: r for r in csv.DictReader(open(os.path.join(HERE, "list.csv"), encoding="utf-8"))}
    ids = a.ids or sorted(d for d in os.listdir(CASES) if os.path.isdir(os.path.join(CASES, d)))
    rows = []
    for cid in ids:
        d = os.path.join(CASES, cid)
        meta = json.load(open(os.path.join(d, "meta.json"), encoding="utf-8"))
        assert meta["id"] == cid and cid in cases, cid
        old_py, new_py = envs[cases[cid]["library"].lower()]
        old_code = open(os.path.join(d, "old.py"), encoding="utf-8").read()
        fixed_code = open(os.path.join(d, "fixed.py"), encoding="utf-8").read()
        c1, _, _ = run(old_py, d, "old.py")
        c2_pass, error, line_no = run(new_py, d, "old.py")
        c2 = not c2_pass and not error.startswith("AssertionError")
        c3, fix_error, _ = run(new_py, d, "fixed.py")
        wrong = "none"
        if os.path.exists(os.path.join(d, "wrong.py")):
            wrong_code = open(os.path.join(d, "wrong.py"), encoding="utf-8").read()
            if not run(new_py, d, "wrong.py")[0]:
                wrong = "caught by the test"
            elif check(wrong_code, old_code):
                wrong = "caught by the validity checks"
            else:
                wrong = "NOT caught"
        leak = "by hand" if cid in REVIEW else ("yes" if matches(cid, old_code) else "no")
        invalid = check(fixed_code, old_code)
        admitted = c1 and c2 and c3 and wrong != "NOT caught" and leak != "yes" and not invalid
        failing_line = old_code.splitlines()[line_no - 1].strip() if line_no else ""
        rows.append({"id": cid, "library": cases[cid]["library"], "old_passes_in_old": c1,
                     "old_fails_in_new": c2, "fix_passes_in_new": c3, "wrong_fix": wrong, "leak": leak,
                     "fix_validity": "; ".join(invalid) or "valid", "admitted": admitted,
                     "failing_line": failing_line, "error": error, "fix_error": "" if c3 else fix_error})
        mark = "ok " if admitted else "-- "
        print(f"{mark}{cid}  1={c1!s:5} 2={c2!s:5} 3={c3!s:5} wrong={wrong:29} leak={leak:7} "
              f"| {failing_line[:50]}")
    out = os.path.join(HERE, "results", "checks.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    old_rows = []
    if os.path.exists(out) and a.ids:
        old_rows = [r for r in csv.DictReader(open(out, encoding="utf-8")) if r["id"] not in set(ids)]
    all_rows = sorted(old_rows + rows, key=lambda r: (r["id"][0] == "N", r["id"]))
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(all_rows)
    print(f"admitted {sum(r['admitted'] for r in rows)} of {len(rows)} -> {os.path.abspath(out)}")


if __name__ == "__main__":
    main()
