"""Re-run the minimal call of every candidate change in its old and new environment (Section 3.2.2).

pandas changes:  old = pandas 1.5.3 + NumPy 1.23.5,  new = pandas 2.2.3 + NumPy 1.23.5
NumPy changes:   old = pandas 2.2.3 + NumPy 1.23.5,  new = pandas 2.2.3 + NumPy 2.1.3
All environments use Python 3.11.

For each change it records whether the call raises, changes its result silently, or behaves the same,
the full library error message, the deprecation warnings of the old version, and whether the
replacement gives the same values as the old call. Output: results/candidates.json
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from candidates_spec import SETUP, SPEC  # noqa: E402

PATH_RE = re.compile(r"\(/[^)]*site-packages/[^)]*\)")


def run(python, code, mode):
    p = subprocess.run([python, os.path.join(HERE, "harness.py")],
                       input=json.dumps({"code": SETUP + code, "mode": mode}),
                       capture_output=True, text=True, timeout=180)
    try:
        out = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:  # noqa: BLE001
        out = {"status": "harness-failure", "stderr": p.stderr[-2000:]}
    if out.get("message"):
        out["message"] = PATH_RE.sub("(<site-packages path>)", out["message"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env-old", required=True, help="python of pandas 1.5.3 + NumPy 1.23.5")
    ap.add_argument("--env-mid", required=True, help="python of pandas 2.2.3 + NumPy 1.23.5")
    ap.add_argument("--env-new", required=True, help="python of pandas 2.2.3 + NumPy 2.1.3")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "results", "candidates.json"))
    a = ap.parse_args()
    envs = {"pandas": (a.env_old, a.env_mid), "numpy": (a.env_mid, a.env_new)}

    rows = []
    for s in SPEC:
        lib = "pandas" if s["id"].startswith("P") else "numpy"
        old_py, new_py = envs[lib]
        mode = s.get("mode", "values")
        old = run(old_py, s["code"], mode)
        new = run(new_py, s["code"], mode)
        if old["status"] != "ok":
            kind = "BROKEN-IN-OLD"
        elif new["status"] == "error":
            kind = "raises"
        elif new["status"] == "ok":
            kind = "same" if json.dumps(old["result"], sort_keys=True) == json.dumps(new["result"], sort_keys=True) else "silent"
        else:
            kind = "HARNESS-FAILURE"
        alt = None
        if s.get("alt"):
            r = run(new_py, s["alt"], mode)
            if r["status"] != "ok":
                alt = "replacement fails: " + r.get("message", r.get("stderr", ""))[:200]
            elif old["status"] == "ok":
                alt = "same values" if json.dumps(r["result"], sort_keys=True) == json.dumps(old["result"], sort_keys=True) else "DIFFERENT values"
        rows.append(dict(id=s["id"], library=lib, kind=kind,
                         new_message=new.get("message"), old_warnings=old.get("warnings", []),
                         old_result=old.get("result"), new_result=new.get("result"), replacement=alt,
                         old_error=old.get("message") if old["status"] != "ok" else None))
        print(f"{s['id']}  {kind:7s}  replacement: {alt}  |  {(new.get('message') or '')[:70]}")

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(rows, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(f"\nSaved {len(rows)} changes to {os.path.abspath(a.out)}")


if __name__ == "__main__":
    main()
