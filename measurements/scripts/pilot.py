"""Re-run the 9-case pilot (Chapter 5) under Python 3.11.

For each case:
  1. old code   + old environment -> tests pass
  2. old code   + new environment -> tests fail (the error message is recorded, including any
                                     interpreter "Did you mean" suggestion)
  3. reference fix + new environment -> tests pass
  4. wrong fix (if any) + new environment -> tests fail
pandas cases: old = pandas 1.5.3 + NumPy 1.23.5, new = pandas 2.2.3 + NumPy 1.23.5
NumPy cases:  old = pandas 2.2.3 + NumPy 1.23.5, new = pandas 2.2.3 + NumPy 2.1.3
Output: results/pilot.json
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.join(HERE, "..", "pilot_cases")
HINT = re.compile(r"\b(use|instead)\b|might want to try", re.I)


def run(python, case_dir, candidate):
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(os.path.join(case_dir, candidate), os.path.join(tmp, "solution.py"))
        shutil.copy(os.path.join(case_dir, "test.py"), os.path.join(tmp, "test.py"))
        p = subprocess.run([python, "-W", "ignore", "test.py"], cwd=tmp, capture_output=True, text=True, timeout=120)
        passed = p.returncode == 0 and "PASS" in p.stdout
        lines = [l.rstrip() for l in p.stderr.strip().splitlines() if l.strip()]
        start = max([i for i, l in enumerate(lines) if re.match(r"^[A-Za-z_][\w.]*(Error|Exception)\b", l)] or [len(lines) - 1])
        return passed, " ".join(l.strip() for l in lines[start:]) if lines else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env-old", required=True)
    ap.add_argument("--env-mid", required=True)
    ap.add_argument("--env-new", required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "..", "results", "pilot.json"))
    a = ap.parse_args()
    env = {"pandas": (os.path.abspath(a.env_old), os.path.abspath(a.env_mid)),
           "numpy": (os.path.abspath(a.env_mid), os.path.abspath(a.env_new))}
    rows = []
    for cid in sorted(os.listdir(CASES)):
        d = os.path.join(CASES, cid)
        meta = json.load(open(os.path.join(d, "meta.json")))
        old_py, new_py = env[meta["library"].lower()]
        old_ok, _ = run(old_py, d, "old.py")
        new_ok, err = run(new_py, d, "old.py")
        fix_ok, _ = run(new_py, d, "fixed.py")
        wrong = None
        if os.path.exists(os.path.join(d, "wrong.py")):
            wrong = "caught" if not run(new_py, d, "wrong.py")[0] else "NOT caught"
        library_msg = err.split(". Did you mean")[0]
        rows.append(dict(case=cid, **meta, old_env_pass=old_ok, new_env_fail=not new_ok, fix_pass=fix_ok,
                         wrong_fix=wrong, verified=old_ok and not new_ok and fix_ok, error=err,
                         raises=not err.startswith("AssertionError"), has_hint=bool(HINT.search(library_msg)),
                         did_you_mean=("Did you mean" in err)))
        print(f"{cid:26s} verified={rows[-1]['verified']!s:5s} wrong_fix={wrong}  | {err[:90]}")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(rows, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(f"Verified {sum(r['verified'] for r in rows)}/{len(rows)} cases -> {os.path.abspath(a.out)}")


if __name__ == "__main__":
    main()
