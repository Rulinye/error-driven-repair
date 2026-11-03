"""Summary of the runs (Section 6.1) and of the failures and warnings (Section 6.6).

usage: python analysis/runs.py [--out analysis/runs.txt]

For each model and each set of runs: the samples and distinct samples, their outcomes, the replies without a code
block with the reason the reply stopped, the cost of the API calls and the GPU time, all read from
runs/results/<model><suffix>/ and probe/results/<model>/. Then, for the main runs: the fixes that pass the tests but
fail only the validity checks, the fixes that fail because they import an optional package, the correct samples
that trigger a warning from the library (Section 3.9) together with the warnings of the reference fixes of the
same test cases, and the replies of Gemini 3.8 Flash without a code block.
"""
import argparse
import csv
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
RESULTS = os.path.join(ROOT, "runs", "results")
sys.path.insert(0, os.path.join(ROOT, "runs"))
from score import case_dir, run_test  # noqa: E402

MODELS = ["gpt-6-luna", "gemini-3.8-flash", "qwen2.5-coder-7b", "codellama-7b"]
SETS = [("", "main runs"), ("-synthetic", "synthetic test cases"), ("-paraphrase", "paraphrased template"),
        ("-second", "second test cases")]
NEW_ENV = {"P": "mid", "N": "new"}


def distinct(folder):
    rows = {}
    for r in csv.DictReader(open(os.path.join(RESULTS, folder, "samples.csv"), encoding="utf-8")):
        rows.setdefault((r["prompt_id"], r["sample"]), r)
    return list(rows.values())


def metas(pattern):
    """Distinct .meta.json files (one call file can be imported into several folders)."""
    seen = {}
    for f in sorted(glob.glob(pattern)):
        m = json.load(open(f))
        seen.setdefault((m.get("first_call"), m.get("calls"), m.get("gpu_seconds")), m)
    return list(seen.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "runs.txt"))
    out = []
    a = ap.parse_args()

    out.append("Runs: distinct samples and their outcomes; replies without a code block by the reason the reply stopped")
    for m in MODELS:
        out.append(f"  {m}")
        for suffix, name in SETS:
            d = distinct(m + suffix)
            oc = Counter(r["outcome"] for r in d)
            stops = Counter(r["stop"] for r in d if r["outcome"] == "no code block")
            out.append(f"    {name:22} distinct samples {len(d):5}  " +
                       ", ".join(f"{k} {v}" for k, v in sorted(oc.items())) +
                       (f"  | no code block by stop reason: {dict(sorted(stops.items()))}" if stops else ""))

    out += ["", "Cost of the API calls (USD) and GPU time (minutes), from the .meta.json files"]
    stages = [("preparation (smoke test, dry run, speed test)", ["-smoke", "-default-smoke", "-dryrun", "-speedtest"]),
              ("knowledge probe", None), ("main runs", [""]),
              ("later runs (synthetic, paraphrased, second)", ["-synthetic", "-paraphrase", "-second"])]
    for m in MODELS:
        total = [0.0, 0.0]
        plan = [0.0, 0.0]
        parts = []
        for name, suffixes in stages:
            if suffixes is None:
                files = metas(os.path.join(ROOT, "probe", "results", m, "*.meta.json"))
            else:
                files = []
                for sfx in suffixes:
                    files += metas(os.path.join(RESULTS, m + sfx, "*.meta.json"))
                files = list({(f.get("first_call"), f.get("calls"), f.get("gpu_seconds")): f for f in files}.values())
            cost = sum(f.get("cost", 0) for f in files)
            gpu = sum(f.get("gpu_seconds", 0) for f in files) / 60
            total = [total[0] + cost, total[1] + gpu]
            if not name.startswith("preparation"):
                plan = [plan[0] + cost, plan[1] + gpu]
            parts.append(f"{name}: {cost:.4f} USD, {gpu:.1f} min")
        out.append(f"  {m}")
        out += [f"    {p}" for p in parts]
        out.append(f"    probe, main and later runs: {plan[0]:.4f} USD, {plan[1]:.1f} min ({plan[1] / 60:.1f} h); "
                   f"everything: {total[0]:.4f} USD, {total[1]:.1f} min")

    out += ["", "Main runs: fixes that pass the tests but fail only the validity checks (distinct samples)"]
    for m in MODELS:
        for r in distinct(m):
            if r["outcome"] == "fails the validity checks":
                out.append(f"  {m:18} {r['case']} {r['condition']} sample {r['sample']}: {r['violations']}")

    out += ["", "Main runs: fixes that fail because they import a package that the environments do not contain"]
    for m in MODELS:
        for j in map(json.loads, open(os.path.join(RESULTS, m, "judged.jsonl"))):
            g = re.search(r"No module named '([^'.]+)", j["error"] or "")
            if g and g.group(1) not in ("solution", "pandas", "numpy"):
                out.append(f"  {m:18} {j['case']} {j['code_hash']}: {g.group(0)}")

    out += ["", "Main runs: correct samples that trigger a warning from the library (Section 3.9)"]
    cases = set()
    for m in MODELS:
        d = [r for r in distinct(m) if r["outcome"] == "correct"]
        w = [r for r in d if r["warnings"]]
        by_case = Counter((r["case"], r["warnings"]) for r in w)
        cases |= {c for c, _ in by_case}
        out.append(f"  {m:18} {len(w)} of {len(d)} correct samples ({100 * len(w) / len(d):.1f}%): " +
                   ", ".join(f"{c} {k} {v}" for (c, k), v in sorted(by_case.items())))
    envs = os.path.abspath(os.path.join(ROOT, "measurements", "envs"))
    out.append("  warnings of the reference fixes of these test cases:")
    for c in sorted(cases):
        python = os.path.join(envs, NEW_ENV[c[0]], "bin", "python")
        passed, _, warnings = run_test(python, c, open(os.path.join(case_dir(c), "fixed.py"), encoding="utf-8").read())
        out.append(f"    {c}: passes {passed}, warnings: {warnings or 'none'}")

    out += ["", "Main runs of gemini-3.8-flash: replies without a code block"]
    replies = {(r["prompt_id"], str(r["sample"])): r for r in map(json.loads, open(os.path.join(RESULTS, "gemini-3.8-flash",
                                                                                                    "replies.jsonl")))}
    for r in distinct("gemini-3.8-flash"):
        if r["outcome"] == "no code block":
            x = replies[(r["prompt_id"], r["sample"])]
            text = (x["text"] or "").strip()
            out.append(f"  {r['case']} {r['condition']} stop {x['stop']:10} output tokens {x['output_tokens']:5} "
                       f"(thinking {x['reasoning_tokens']:5})  text: {len(text):4} characters  "
                       f"{json.dumps(text[:60], ensure_ascii=False)}")

    text = "\n".join(out) + "\n"
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(text, end="")


if __name__ == "__main__":
    main()
