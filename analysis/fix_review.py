"""Review of a random sample of correct fixes (Section 3.9).

usage: python analysis/fix_review.py draw      # writes analysis/fix_review_sample.csv
       python analysis/fix_review.py summary   # checks analysis/fix_review.csv, writes analysis/fix_review.txt

The population of a model is the distinct fixes of its main runs (90 test cases, 20 conditions, main
template) that are judged correct, one per (test case, code): at temperature 0.2 the same code often recurs,
and each one is read once. For each model, in the order GPT-6 Luna, Gemini 3.8 Flash, Qwen2.5-Coder-7B,
CodeLlama-7B, 25 fixes are drawn with random.Random(20261106).sample (one Random object for the four draws)
from the population sorted by test case (in the order of runs/prompts.py) and code hash.

Each sampled fix is read in full and labelled in analysis/fix_review.csv:
  correct       gives the result of the old version in general, not only on the test input;
  wrong         passes the test, but gives a different result than the old version on other inputs;
  hard-coded    returns fixed values for the test input or treats it as a special case.
A fix is compared with the old version on the inputs that the function takes, not only on the usual ones.
Where the reference fix itself gives a different result than the old version (for example, datetimes in
seconds instead of nanoseconds), a fix may give either. Where this was not clear from reading the fix, the
function was run on further inputs (analysis/fix_review_probes/, output in analysis/fix_review_probes.txt).
There is no second rater, so no agreement statistic is computed.
"""
import argparse
import csv
import hashlib
import json
import os
import random
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "runs"))
from prompts import Conditions  # noqa: E402
from score import extract  # noqa: E402

MODELS = ["gpt-6-luna", "gemini-3.8-flash", "qwen2.5-coder-7b", "codellama-7b"]
PER_MODEL = 25
SEED = 20261106
LABELS = ("correct", "wrong", "hard-coded")


def code_hash(code):
    return hashlib.sha256((code if code is not None else "\0none").encode()).hexdigest()[:16]


def population(model, order):
    folder = os.path.join(ROOT, "runs", "results", model)
    correct = {(j["case"], j["code_hash"]) for j in map(json.loads, open(os.path.join(folder, "judged.jsonl")))
               if j["correct"]}
    conditions = defaultdict(set)
    rows = {(r["prompt_id"], r["sample"]): r for r in csv.DictReader(open(os.path.join(folder, "samples.csv"),
                                                                          encoding="utf-8"))}
    for rep in map(json.loads, open(os.path.join(folder, "replies.jsonl"))):
        key = (rep["case"], code_hash(extract(rep["text"] or "")))
        row = rows.get((rep["prompt_id"], str(rep["sample"])))
        if key in correct and row is not None:
            conditions[key].add(row["condition"])
    assert set(conditions) == correct, model
    return sorted(correct, key=lambda k: (order[k[0]], k[1])), conditions


def draw(seed, out):
    order = {c: i for i, c in enumerate(Conditions().cases)}
    rng = random.Random(seed)
    rows = []
    for m in MODELS:
        pop, conditions = population(m, order)
        for case, h in rng.sample(pop, PER_MODEL):
            rows.append({"model": m, "case": case, "code_hash": h, "population": len(pop),
                         "conditions": " ".join(sorted(conditions[(case, h)]))})
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} fixes -> {os.path.relpath(out, ROOT)}")


def summary():
    sample = list(csv.DictReader(open(os.path.join(HERE, "fix_review_sample.csv"), encoding="utf-8")))
    labels = {(r["model"], r["case"], r["code_hash"]): r for r in
              csv.DictReader(open(os.path.join(HERE, "fix_review.csv"), encoding="utf-8"))}
    keys = [(r["model"], r["case"], r["code_hash"]) for r in sample]
    assert set(labels) == set(keys), "fix_review.csv must label exactly the sampled fixes"
    assert all(labels[k]["label"] in LABELS for k in keys)
    lines = ["Review of a random sample of correct fixes (Section 3.9): 25 distinct correct fixes per model, "
             f"seed {SEED}; one rater, so no agreement statistic.", ""]
    for m in MODELS:
        c = Counter(labels[k]["label"] for k in keys if k[0] == m)
        pop = next(r["population"] for r in sample if r["model"] == m)
        lines.append(f"  {m:17} population {pop:>4}  " + "  ".join(f"{x} {c[x]:2d}" for x in LABELS))
    total = Counter(labels[k]["label"] for k in keys)
    lines.append(f"  {'all':17} {'':15}  " + "  ".join(f"{x} {total[x]:2d}" for x in LABELS))
    flagged = [k for k in keys if labels[k]["label"] != "correct"]
    if flagged:
        lines += ["", "Fixes not labelled correct:"]
        lines += [f"  {m} {c} {h}: {labels[(m, c, h)]['label']}: {labels[(m, c, h)]['reason']}" for m, c, h in flagged]
    text = "\n".join(lines) + "\n"
    with open(os.path.join(HERE, "fix_review.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text, end="")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["draw", "summary"])
    ap.add_argument("--seed", type=int, default=SEED, help=argparse.SUPPRESS)  # for testing the script only
    ap.add_argument("--out", default=os.path.join(HERE, "fix_review_sample.csv"), help=argparse.SUPPRESS)
    a = ap.parse_args()
    draw(a.seed, a.out) if a.step == "draw" else summary()


if __name__ == "__main__":
    main()
