"""Rule-based baseline for RQ1 (Section 3.10): Ruff on the 90 test cases, judged like a model's fix.

usage: python analysis/ruff_baseline.py [--out analysis/ruff.csv]

Ruff (measurements/envs/tools, 0.16.10) runs with the NumPy rules NPY001, NPY003 and NPY201 and the pandas
rules (PD) on the old program of every test case, first to report (a case is detected if Ruff reports any of
these rules), then with its safe automatic fixes (no unsafe fixes). The fixed program is judged by
runs/score.py like a model's fix: the test in the new environment and the validity checks. Writes ruff.csv
(one row per test case) and ruff.txt (counts by library, next to pass@1 under E0·D0 of every model).
"""
import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "runs"))
from prompts import Conditions  # noqa: E402
from score import judge  # noqa: E402

ENVS = os.path.join(ROOT, "measurements", "envs")
RUFF = os.path.join(ENVS, "tools", "bin", "ruff")
RULES = "NPY001,NPY003,NPY201,PD"
MODELS = ["gpt-6-luna", "gemini-3.8-flash", "qwen2.5-coder-7b", "codellama-7b"]


def ruff(args, path):
    return subprocess.run([RUFF, "check", "--no-cache", "--isolated", "--select", RULES, *args, path],
                          capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "ruff.csv"))
    a = ap.parse_args()
    version = subprocess.run([RUFF, "--version"], capture_output=True, text=True).stdout.strip()
    conds = Conditions()
    rows = []
    for cid in conds.cases:
        old = conds.program(cid)
        library = conds.errors[cid]["library"]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "solution.py")
            with open(path, "w", encoding="utf-8") as f:
                f.write(old)
            diags = json.loads(ruff(["--output-format", "json"], path).stdout or "[]")
            ruff(["--fix"], path)
            fixed = open(path, encoding="utf-8").read()
        changed = fixed != old
        j = judge(ENVS, cid, library, f"```python\n{fixed}\n```", old) if changed else None
        rows.append({"id": cid, "library": library, "detected": bool(diags),
                     "rules": " ".join(sorted({d["code"] for d in diags})), "changed": changed,
                     "correct": bool(j and j["correct"]), "outcome": j["outcome"] if j else "not changed"})
        print(f"{cid}  detected={rows[-1]['detected']!s:5} rules={rows[-1]['rules']:14} changed={changed!s:5} "
              f"{rows[-1]['outcome']}", flush=True)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    lines = [f"Ruff baseline (Section 3.10): {version}, rules {RULES}, safe fixes only; 90 test cases.", ""]
    for lib in ("pandas", "NumPy"):
        r = [x for x in rows if x["library"] == lib]
        lines.append(f"{lib:6}  {len(r)} test cases: detected {sum(x['detected'] for x in r)}, "
                     f"changed {sum(x['changed'] for x in r)}, correct {sum(x['correct'] for x in r)}")
    lines.append(f"all     90 test cases: detected {sum(x['detected'] for x in rows)}, "
                 f"changed {sum(x['changed'] for x in rows)}, correct {sum(x['correct'] for x in rows)}")
    lines.append("")
    lines.append("RQ1: pass@1 under E0·D0 (mean over the test cases of a library, in %), and Ruff's share correct")
    for lib in ("pandas", "NumPy", "all"):
        ids = [x["id"] for x in rows if lib == "all" or x["library"] == lib]
        parts = []
        for model in MODELS:
            correct = {}
            with open(os.path.join(ROOT, "runs", "results", model, "samples.csv"), newline="", encoding="utf-8") as f:
                for s in csv.DictReader(f):
                    if s["condition"] == "E0D0" and s["template"] == "main" and s["case"] in ids:
                        correct.setdefault(s["case"], []).append(s["correct"] == "True")
            assert len(correct) == len(ids)
            parts.append(f"{model} {100 * sum(sum(v) / len(v) for v in correct.values()) / len(ids):5.1f}")
        ruff_share = 100 * sum(x["correct"] for x in rows if x["id"] in ids) / len(ids)
        lines.append(f"  {lib:6} ({len(ids):2d})  " + "  ".join(parts) + f"  Ruff {ruff_share:5.1f}")
    text = "\n".join(lines) + "\n"
    with open(os.path.join(HERE, "ruff.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text, end="")


if __name__ == "__main__":
    main()
