"""Run Ruff on the 9 pilot cases (Section 5.5): which cases it detects and which it fixes.

Ruff 0.16.10, rules NPY (NumPy) and PD (pandas), safe automatic fixes only.
A case counts as fixed when Ruff changed the file AND the changed file passes the case's test
in the new environment. Output: results/ruff.json
"""
import argparse
import json
import os
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.join(HERE, "..", "pilot_cases")


def test_passes(python, case_dir, path):
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(path, os.path.join(tmp, "solution.py"))
        shutil.copy(os.path.join(case_dir, "test.py"), os.path.join(tmp, "test.py"))
        p = subprocess.run([python, "-W", "ignore", "test.py"], cwd=tmp, capture_output=True, text=True, timeout=120)
        return p.returncode == 0 and "PASS" in p.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ruff", required=True)
    ap.add_argument("--env-mid", required=True)
    ap.add_argument("--env-new", required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "..", "results", "ruff.json"))
    a = ap.parse_args()
    version = subprocess.run([a.ruff, "--version"], capture_output=True, text=True).stdout.strip()
    rows = []
    for cid in sorted(os.listdir(CASES)):
        d = os.path.join(CASES, cid)
        meta = json.load(open(os.path.join(d, "meta.json")))
        new_py = os.path.abspath(a.env_mid if meta["library"].lower() == "pandas" else a.env_new)
        with tempfile.TemporaryDirectory() as tmp:
            f = os.path.join(tmp, "case.py")
            shutil.copy(os.path.join(d, "old.py"), f)
            p = subprocess.run([a.ruff, "check", "--no-cache", "--select", "NPY,PD", "--output-format", "json", f],
                               capture_output=True, text=True)
            diags = json.loads(p.stdout or "[]")
            before = open(f).read()
            subprocess.run([a.ruff, "check", "--no-cache", "--select", "NPY,PD", "--fix", f], capture_output=True, text=True)
            after = open(f).read()
            changed = after != before
            fixed = changed and test_passes(new_py, d, f)
        rows.append(dict(case=cid, detected=bool(diags), rules=sorted({x["code"] for x in diags}),
                         changed=changed, fixed=fixed))
        print(f"{cid:26s} detected={bool(diags)!s:5s} rules={rows[-1]['rules']} changed={changed} fixed={fixed}")
    out = dict(ruff_version=version, cases=rows)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(f"{version}: detected {sum(r['detected'] for r in rows)}, fixed {sum(r['fixed'] for r in rows)} -> {os.path.abspath(a.out)}")


if __name__ == "__main__":
    main()
