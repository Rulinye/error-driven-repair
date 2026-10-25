"""Run the old code and the replacement of each pool row in pool_spec.py (criterion 2 and the
replacement check).

usage: python screening/run_pool_checks.py
Uses the environments of measurements/ (as in measurements/run_all.sh) and the harness
measurements/scripts/harness.py. Writes results/pool_checks.csv.

pandas rows:  old = pandas 1.5.3 + NumPy 1.23.5,  new = pandas 2.2.3 + NumPy 1.23.5
NumPy rows:   old = pandas 2.2.3 + NumPy 1.23.5,  new = pandas 2.2.3 + NumPy 2.1.3

  kind         raises (runs in the old version, raises in the new one), silent (runs in both, result
               differs), same (runs in both, same result), or broken in old (fails in the old version)
  replacement  same values, different values, or fails (run in the new version and compared with the
               result of the old code in the old version)
"""
import csv
import json
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

from pool_spec import SETUP, SPEC

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
ENVS = os.path.join(ROOT, "measurements", "envs")
HARNESS = os.path.join(ROOT, "measurements", "scripts", "harness.py")
PATH_RE = re.compile(r"(/[^\s'\"()]*)?site-packages/[^\s'\"()]*")


def python(env):
    return os.path.join(ENVS, env, "bin", "python")


def library(key):
    return "numpy" if key.startswith(("numpy", "generic.", "ndarray.", "finfo.")) else "pandas"


def run(env, code, mode):
    p = subprocess.run([python(env), HARNESS], input=json.dumps({"code": SETUP + code, "mode": mode}),
                       capture_output=True, text=True, timeout=300, cwd=HERE)
    try:
        out = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:  # noqa: BLE001
        out = {"status": "harness failure", "message": p.stderr[-500:], "warnings": []}
    for k in ("message",):
        if out.get(k):
            out[k] = PATH_RE.sub("<site-packages path>", out[k])
    out["warnings"] = [PATH_RE.sub("<site-packages path>", w) for w in out.get("warnings", [])]
    return out


def check(item):
    key, spec = item
    old_env, new_env = ("old", "mid") if library(key) == "pandas" else ("mid", "new")
    old = run(old_env, spec["code"], spec["mode"])
    new = run(new_env, spec["code"], spec["mode"])
    same = lambda a, b: json.dumps(a.get("result"), sort_keys=True) == json.dumps(b.get("result"), sort_keys=True)  # noqa: E731
    if old["status"] != "ok":
        kind = "broken in old"
    elif new["status"] == "error":
        kind = "raises"
    elif new["status"] == "ok":
        kind = "same" if same(old, new) else "silent"
    else:
        kind = new["status"]
    replacement = ""
    if spec["alt"] is not None:
        alt = run(new_env, spec["alt"], spec["mode"])
        if alt["status"] != "ok":
            replacement = "fails: " + (alt.get("message") or "")[:200]
        elif old["status"] == "ok":
            replacement = "same values" if same(old, alt) else "different values"
    return {"key": key, "library": library(key), "kind": kind, "replacement": replacement,
            "new_error": (new.get("message") or "")[:300] if new["status"] == "error" else "",
            "old_error": (old.get("message") or "")[:300] if old["status"] != "ok" else "",
            "old_warnings": " | ".join(old.get("warnings", []))[:600],
            "old_code": spec["code"], "replacement_code": spec["alt"] or ""}


def main():
    with ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(check, SPEC.items()))
    path = os.path.join(HERE, "results", "pool_checks.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    counts = {}
    for r in rows:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    print(f"{len(rows)} rows run -> {path}")
    for k, v in sorted(counts.items()):
        print(f"  {k:14s} {v}")


if __name__ == "__main__":
    main()
