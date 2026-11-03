"""Further inputs for the review of correct fixes (Section 3.9, analysis/fix_review.py).

usage: python analysis/fix_review_probes/run.py
Run from the repository root after `bash measurements/run_all.sh` has built the environments.

Where it was not clear from reading whether a sampled fix gives the result of the old version, <id>.py calls
the function of test case <id> on further inputs. Each probe is run with the old program in the old
environment, and with the reference fix and every sampled fix of that test case in the new environment (as in
test_cases/check_cases.py). Writes analysis/fix_review_probes.txt.
"""
import csv
import glob
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ANALYSIS = os.path.dirname(HERE)
ROOT = os.path.dirname(ANALYSIS)
sys.path.insert(0, ANALYSIS)
from fix_review import Conditions, code_hash, extract  # noqa: E402

ENVS = os.path.join(ROOT, "measurements", "envs")


def run(env, code, probe):
    with tempfile.TemporaryDirectory() as tmp:
        for name, text in (("solution.py", code), ("probe.py", probe)):
            with open(os.path.join(tmp, name), "w", encoding="utf-8") as f:
                f.write(text)
        r = subprocess.run([os.path.join(ENVS, env, "bin", "python"), "-W", "ignore", "probe.py"], cwd=tmp,
                           capture_output=True, text=True, timeout=300)
        out = r.stdout.rstrip()
        if r.returncode:
            out += "\n" + (r.stderr.strip().splitlines() or ["(no message)"])[-1]
        return out.replace(tmp, "<tmp>")


def fix(model, case, h):
    for rep in map(json.loads, open(os.path.join(ROOT, "runs", "results", model, "replies.jsonl"))):
        if rep["case"] == case:
            code = extract(rep["text"] or "")
            if code_hash(code) == h:
                return code
    raise KeyError((model, case, h))


def main():
    sample = list(csv.DictReader(open(os.path.join(ANALYSIS, "fix_review_sample.csv"), encoding="utf-8")))
    order = {c: i for i, c in enumerate(Conditions().cases)}
    probes = sorted((os.path.basename(p)[:-3] for p in glob.glob(os.path.join(HERE, "[PN][0-9][0-9].py"))),
                    key=order.__getitem__)
    lines = ["Further inputs for the review of correct fixes (Section 3.9): the old program in the old environment,",
             "then the reference fix and each sampled fix in the new environment.", ""]
    for case in probes:
        probe = open(os.path.join(HERE, f"{case}.py"), encoding="utf-8").read()
        new = "new" if case.startswith("N") else "mid"
        folder = os.path.join(ROOT, "test_cases", "cases", case)
        lines += [f"### {case}", "--- old program",
                  run("old", open(os.path.join(folder, "old.py"), encoding="utf-8").read(), probe),
                  "--- reference fix", run(new, open(os.path.join(folder, "fixed.py"), encoding="utf-8").read(), probe)]
        for r in sample:
            if r["case"] == case:
                lines += [f"--- {r['model']} {r['code_hash']}", run(new, fix(r["model"], case, r["code_hash"]), probe)]
        lines.append("")
        print(case)
    with open(os.path.join(ANALYSIS, "fix_review_probes.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"{len(probes)} test cases -> analysis/fix_review_probes.txt")


if __name__ == "__main__":
    main()
