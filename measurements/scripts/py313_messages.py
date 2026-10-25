"""How the error messages of the 82 erroring changes look under Python 3.13 (Chapter 7).

The thesis fixes Python 3.11, the newest Python on which all three library combinations install.
A project that is forced to upgrade, however, typically moves to Python 3.13, the first Python
that requires pandas 2.2.3 and NumPy 2.1. This script runs the minimal call of each erroring
change WITHOUT catching the exception, so the interpreter prints the message exactly as a user
sees it (including any "Did you mean" suggestion), once in the Python 3.11 environment of the
study and once under Python 3.13 with pandas 2.2.3 + NumPy 2.1.3, and compares the two.

Python 3.11 side: pandas changes -> pandas 2.2.3 + NumPy 1.23.5; NumPy changes -> pandas 2.2.3 + NumPy 2.1.3.
For every keyword-argument error that gains a suggestion under 3.13, it also follows the suggestion
(renames the argument, keeps its value) and checks the result against the old version's result
from results/candidates.json: "same as old", "fails", or "different result".
Output: results/py313.json
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
from candidates_spec import SETUP, SPEC  # noqa: E402
from changes import is_planned, load_changes  # noqa: E402

CODE = {s["id"]: s["code"] for s in SPEC}
PATH_RE = re.compile(r"\(/[^)]*site-packages/[^)]*\)")


def erroring_ids():
    """The 82 planned changes that raise an error."""
    return [cid for cid, row in load_changes().items() if is_planned(row) and row["observed"] == "raises"]


def printed_error(python, code):
    """Run the code uncaught and return the exception text the interpreter prints (no stack frames)."""
    p = subprocess.run([python, "-W", "ignore", "-c", SETUP + code], capture_output=True, text=True, timeout=180)
    err = p.stderr
    if "Traceback (most recent call last):" not in err:
        return "(no error)"
    block = err.rsplit("Traceback (most recent call last):", 1)[1].splitlines()[1:]
    i = 0
    while i < len(block) and (block[i].startswith("  ") or not block[i].strip()):
        i += 1
    text = "\n".join(block[i:]).strip()
    return PATH_RE.sub("(<site-packages path>)", text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env-mid", required=True, help="Python 3.11, pandas 2.2.3 + NumPy 1.23.5")
    ap.add_argument("--env-new", required=True, help="Python 3.11, pandas 2.2.3 + NumPy 2.1.3")
    ap.add_argument("--env-py313", required=True, help="Python 3.13, pandas 2.2.3 + NumPy 2.1.3")
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "py313.json"))
    a = ap.parse_args()
    ver = subprocess.run([a.env_py313, "-c", "import sys, pandas, numpy; print(sys.version.split()[0], pandas.__version__, numpy.__version__)"],
                         capture_output=True, text=True).stdout.split()
    rows = {}
    for cid in erroring_ids():
        py311 = a.env_new if cid.startswith("N") else a.env_mid
        m311 = printed_error(py311, CODE[cid])
        m313 = printed_error(a.env_py313, CODE[cid])
        sugg = re.search(r"Did you mean:? '?([^'?]+)'?\??\s*$", m313)
        rows[cid] = dict(py311=m311, py313=m313, differs=m311 != m313,
                         new_suggestion=(sugg.group(1) if sugg and "Did you mean" not in m311 else None))
    cand = {r["id"]: r for r in json.load(open(os.path.join(ROOT, "results", "candidates.json"), encoding="utf-8"))}
    follow = {}
    for cid, v in rows.items():
        m = re.search(r"unexpected keyword argument '(\w+)'", v["py313"])
        if v["new_suggestion"] and m:
            code = CODE[cid].replace(m.group(1) + "=", v["new_suggestion"] + "=")
            p = subprocess.run([a.env_py313, os.path.join(HERE, "harness.py")],
                               input=json.dumps({"code": SETUP + code, "mode": "values"}),
                               capture_output=True, text=True, timeout=180)
            r = json.loads(p.stdout.strip().splitlines()[-1])
            if r.get("status") != "ok":
                follow[cid] = "fails"
            else:
                same = json.dumps(r["result"], sort_keys=True) == json.dumps(cand[cid]["old_result"], sort_keys=True)
                follow[cid] = "same as old" if same else "different result"
    diff = [k for k, v in rows.items() if v["differs"]]
    out = dict(python313_env=dict(zip(("python", "pandas", "numpy"), ver)), n=len(rows),
               differ=diff, new_suggestion={k: rows[k]["new_suggestion"] for k in diff if rows[k]["new_suggestion"]},
               follow_keyword_suggestion=follow, changes=rows)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(f"Python 3.13 env: {out['python313_env']}")
    print(f"{len(rows)} erroring changes; {len(diff)} messages differ between Python 3.11 and 3.13")
    for k in diff:
        print(f"\n{k}\n  3.11: {rows[k]['py311'][-160:]}\n  3.13: {rows[k]['py313'][-160:]}")
        if k in follow:
            print(f"  following the 3.13 suggestion: {follow[k]}")


if __name__ == "__main__":
    main()
