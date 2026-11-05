"""Review of a random sample of correct fixes (Section 3.9).

usage: python analysis/fix_review.py draw      # writes analysis/fix_review_sample.csv
       python analysis/fix_review.py summary   # checks fix_review.csv and fix_review_second.csv, writes fix_review.txt

The population of a model is the distinct fixes of its main runs (90 test cases, 20 conditions, main
template) that are judged correct, one per (test case, code): at temperature 0.2 the same code often recurs,
and each one is read once. For each model, in the order GPT-6 Luna, Gemini 3.8 Flash, Qwen2.5-Coder-7B,
CodeLlama-7B, 25 fixes are drawn with random.Random(20261106).sample (one Random object for the four draws)
from the population sorted by test case (in the order of runs/prompts.py) and code hash.

Each sampled fix is read in full and labelled in analysis/fix_review.csv (column label, with the reason):
  correct       gives the result of the old version in general, not only on the test input;
  wrong         passes the test, but gives a different result than the old version on other inputs;
  hard-coded    returns fixed values for the test input or treats it as a special case.
A fix is compared with the old version on the inputs that the function takes, not only on the usual ones.
Where the reference fix itself gives a different result than the old version (for example, datetimes in
seconds instead of nanoseconds), a fix may give either. Where this was not clear from reading the fix, the
function was run on further inputs (analysis/fix_review_probes/, output in analysis/fix_review_probes.txt).

Second rater (added after the review): a second rater, who saw neither these labels nor the model and the condition
of a fix, labelled the same 100 fixes with the same criterion in analysis/fix_review_second.csv: round1 from the
code alone (when unsure, the leaning), round2 after seeing the further inputs, for the 48 fixes of the 22 test
cases that have them, and a short note. The first rater chose these inputs, so round 2 is not independent of the
first labels. Agreement and Cohen's kappa with the first labels are reported for both rounds, with a 95% interval
from resampling the 100 fixes 10,000 times (random.Random(20261107)); a fix without round2 keeps its round1 label.
Where the two raters differ, they agreed on a label (column consensus of fix_review.csv, with consensus_reason
where it differs from the first label); the counts and the weighted estimate use it.

Weighted estimate (added after the review): each distinct fix stands for all the correct samples of the main runs
that contain it, so a fix that a model wrote 100 times counts 100 times. Because the fixes were drawn with equal
probability, the sum of the weights of the fixes that are not correct, divided by the sum of the weights of all
25, estimates the share of correct samples that are not correct. The 95% interval comes from resampling the 25
fixes of a model 10,000 times (random.Random(SEED)); the pooled share weights each model by its correct samples.
As a bound, C1 and C3 of the main runs are recomputed as if the upper end of the interval of a model applied to
the condition with information (E3 or D2) and no fix were wrong under E2 without documentation.
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


def correct_samples(model):
    """Distinct correct samples of the main runs per (test case, code hash), and pass@1 (%) per condition."""
    folder = os.path.join(ROOT, "runs", "results", model)
    rows = list(csv.DictReader(open(os.path.join(folder, "samples.csv"), encoding="utf-8")))
    replies = {(r["prompt_id"], str(r["sample"])): r for r in map(json.loads, open(os.path.join(folder, "replies.jsonl")))}
    weights, done = Counter(), set()
    for r in rows:
        k = (r["prompt_id"], r["sample"])
        if r["outcome"] == "correct" and k not in done:
            done.add(k)
            weights[(r["case"], code_hash(extract(replies[k]["text"] or "")))] += 1
    by_condition = defaultdict(list)
    for r in rows:
        if r["template"] == "main":
            by_condition[r["condition"]].append(r["outcome"] == "correct")
    rates = {c: 100 * sum(v) / len(v) for c, v in by_condition.items()}
    conditions = defaultdict(Counter)  # condition rows per fix, for the primary conditions
    for r in rows:
        if r["outcome"] == "correct" and r["condition"] in ("E2D0", "E3D0", "E4D0", "E2D2", "E3D2", "E4D2"):
            k = (r["prompt_id"], r["sample"])
            conditions[(r["case"], code_hash(extract(replies[k]["text"] or "")))][r["condition"]] += 1
    return weights, rates, conditions


def weighted(lines, sample, labels):
    rng = random.Random(SEED)
    data, ratios = {}, {}
    lines += ["", "Weighted by the correct samples of the main runs that each fix stands for (see the docstring)"]
    wrong_by_condition = Counter()
    for m in MODELS:
        weights, rates, conditions = correct_samples(m)
        fixes = [(r["case"], r["code_hash"]) for r in sample if r["model"] == m]
        w = [weights[f] for f in fixes]
        y = [labels[(m,) + f]["consensus"] != "correct" for f in fixes]
        for f, bad in zip(fixes, y):
            if bad:
                wrong_by_condition.update(conditions[f])
        ratio = sum(a for a, b in zip(w, y) if b) / sum(w)
        boot = []
        for _ in range(10000):
            idx = [rng.randrange(len(w)) for _ in w]
            boot.append(sum(w[i] for i in idx if y[i]) / sum(w[i] for i in idx))
        boot.sort()
        lo, hi = boot[249], boot[9749]
        data[m] = (w, y, sum(weights.values()))
        ratios[m] = (ratio, lo, hi, rates)
        lines.append(f"  {m:17} not correct {100 * ratio:4.1f}% of the correct samples  95% CI [{100 * lo:4.1f}, "
                     f"{100 * hi:4.1f}]  (sampled fixes stand for {sum(w)} of {sum(weights.values())} correct samples)")
    total = sum(d[2] for d in data.values())
    pooled = sum(d[2] * ratios[m][0] for m, d in data.items()) / total
    boot = []
    for _ in range(10000):
        e = 0.0
        for m, (w, y, n) in data.items():
            idx = [rng.randrange(len(w)) for _ in w]
            e += n * sum(w[i] for i in idx if y[i]) / sum(w[i] for i in idx)
        boot.append(e / total)
    boot.sort()
    lines.append(f"  {'all':17} not correct {100 * pooled:4.1f}% of the correct samples  95% CI [{100 * boot[249]:4.1f}, "
                 f"{100 * boot[9749]:4.1f}]  (models weighted by their correct samples)")
    lines += ["", "Bound: C1 and C3 if the upper end of the interval applied to the condition with information only"]
    for m in MODELS:
        ratio, lo, hi, r = ratios[m]
        c1, c3 = r["E3D0"] - r["E2D0"], r["E2D2"] - r["E2D0"]
        lines.append(f"  {m:17} C1 {c1:+5.1f} -> {c1 - hi * r['E3D0']:+5.1f}   C3 {c3:+5.1f} -> {c3 - hi * r['E2D2']:+5.1f}")
    lines += ["", "Correct samples of the fixes that are not correct, by primary condition (all models): " +
              ", ".join(f"{c} {wrong_by_condition[c]}" for c in ("E2D0", "E3D0", "E4D0", "E2D2", "E3D2", "E4D2"))]


def kappa(a, b):
    """Cohen's kappa of two equally long label lists."""
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    cats = set(a) | set(b)
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return po, (po - pe) / (1 - pe) if pe < 1 else float("nan")


def agreement(lines, sample, labels):
    """Second rater: agreement with the first labels in round 1 (independent) and round 2."""
    path = os.path.join(HERE, "fix_review_second.csv")
    if not os.path.exists(path):
        return
    second = {(r["model"], r["case"], r["code_hash"]): r for r in csv.DictReader(open(path, encoding="utf-8"))}
    keys = [(r["model"], r["case"], r["code_hash"]) for r in sample]
    assert set(second) == set(keys), "fix_review_second.csv must label exactly the sampled fixes"
    first = [labels[k]["label"] for k in keys]
    lines += ["", "Second rater: agreement with the first labels (column label); 95% CI from resampling the 100 fixes "
              "(10,000 times, seed 20261107)"]
    for rnd, col in (("round 1 (independent)", "round1"), ("round 2 (after the further inputs, not independent)", "round2")):
        other = [second[k][col] or second[k]["round1"] for k in keys]
        assert all(x in LABELS for x in other)
        po, k = kappa(first, other)
        rng = random.Random(20261107)
        boot = []
        for _ in range(10000):
            idx = [rng.randrange(len(keys)) for _ in keys]
            boot.append(kappa([first[i] for i in idx], [other[i] for i in idx])[1])
        boot = sorted(x for x in boot if x == x)
        lo, hi = boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]
        table = Counter(zip(first, other))
        lines.append(f"  {rnd}: agreement {100 * po:.0f}%, Cohen's kappa {k:.2f} [{lo:.2f}, {hi:.2f}]; "
                     "first/second: " + ", ".join(f"{x}/{y} {v}" for (x, y), v in sorted(table.items())))
        if col == "round1":
            lines += [f"    differs: {m} {c} {h}: first {labels[(m, c, h)]['label']}, second {second[(m, c, h)][col]}"
                      for (m, c, h), x, y in zip(keys, first, other) if x != y]


def summary():
    sample = list(csv.DictReader(open(os.path.join(HERE, "fix_review_sample.csv"), encoding="utf-8")))
    labels = {(r["model"], r["case"], r["code_hash"]): r for r in
              csv.DictReader(open(os.path.join(HERE, "fix_review.csv"), encoding="utf-8"))}
    keys = [(r["model"], r["case"], r["code_hash"]) for r in sample]
    assert set(labels) == set(keys), "fix_review.csv must label exactly the sampled fixes"
    assert all(labels[k]["label"] in LABELS and labels[k]["consensus"] in LABELS for k in keys)
    assert all(bool(labels[k]["consensus_reason"]) == (labels[k]["consensus"] != labels[k]["label"]) for k in keys)
    lines = ["Review of a random sample of correct fixes (Section 3.9): 25 distinct correct fixes per model, "
             f"seed {SEED}; labels agreed by the two raters (column consensus).", ""]
    for m in MODELS:
        c = Counter(labels[k]["consensus"] for k in keys if k[0] == m)
        pop = next(r["population"] for r in sample if r["model"] == m)
        lines.append(f"  {m:17} population {pop:>4}  " + "  ".join(f"{x} {c[x]:2d}" for x in LABELS))
    total = Counter(labels[k]["consensus"] for k in keys)
    lines.append(f"  {'all':17} {'':15}  " + "  ".join(f"{x} {total[x]:2d}" for x in LABELS))
    weighted(lines, sample, labels)
    agreement(lines, sample, labels)
    flagged = [k for k in keys if labels[k]["consensus"] != "correct"]
    if flagged:
        lines += ["", "Fixes not labelled correct:"]
        lines += [f"  {m} {c} {h}: {labels[(m, c, h)]['consensus']}: "
                  f"{labels[(m, c, h)]['consensus_reason'] or labels[(m, c, h)]['reason']}" for m, c, h in flagged]
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
