"""Exploratory and descriptive analyses of the main runs (Section 4.6).

usage: python analysis/exploratory.py [--out analysis/exploratory.txt]

All differences are computed within each change and averaged over the changes, in percentage points, with a
95% cluster-bootstrap interval (analysis/inference.py, seed 20261102); they are not tested.

  1. E0 vs E2 without documentation, separately for the changes whose library message gives a hint and for
     those with an interpreter suggestion; the second group is listed change by change.
  2. E1 vs E2 without documentation: the value of an error message that gives no hint.
  3. D1 vs D2 at each error level, for the changes whose release-note entry names the fix and for those where
     only the old warning does, with recall@3 of the retrieval for each group and level.
  4. D3 vs D2 at each error level: the effect of distractor entries.
  5. Failures under E0 and E4 without documentation: fixes that fail the test and fixes that pass the test but
     fail the validity checks (such as calls to _append).
  6. pass@1 of the primary conditions by library and by type of change.
A condition that a model has not run on every change (Gemini 3.8 Flash stopped at its budget) is reported on
the changes it has, with their number.
"""
import argparse
import csv
import os
from collections import defaultdict

import numpy as np

from inference import counts, resampled_means

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
RESULTS = os.path.join(ROOT, "runs", "results")
MODELS = ["gpt-6-luna", "gemini-3.8-flash", "qwen2.5-coder-7b", "codellama-7b"]
NAMES = {"gpt-6-luna": "GPT-6 Luna", "gemini-3.8-flash": "Gemini 3.8 Flash",
         "qwen2.5-coder-7b": "Qwen2.5-Coder-7B", "codellama-7b": "CodeLlama-7B"}
SEED = 20261102


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load(model):
    """{(case, condition): [correct, ...]} and {(case, condition): [outcome, ...]}."""
    correct, outcome = defaultdict(list), defaultdict(list)
    for r in read(os.path.join(RESULTS, model, "samples.csv")):
        if r["template"] == "main":
            correct[(r["case"], r["condition"])].append(r["correct"] == "True")
            outcome[(r["case"], r["condition"])].append(r["outcome"])
    return correct, outcome


def diff(correct, ids, a, b):
    """Mean within-change difference a - b and its bootstrap interval, over the changes that have both."""
    have = [i for i in ids if len(correct.get((i, a), [])) == 5 and len(correct.get((i, b), [])) == 5]
    if not have:
        return None
    d = 100 * np.array([np.mean(correct[(i, a)]) - np.mean(correct[(i, b)]) for i in have])
    low, high = np.percentile(resampled_means(d[:, None], counts(len(have), seed=SEED))[:, 0], [2.5, 97.5])
    return len(have), d.mean(), low, high


def fmt(r):
    if r is None:
        return "   (not run)"
    n, m, lo, hi = r
    return f"{m:+6.1f} [{lo:+6.1f}, {hi:+6.1f}] (n {n})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "exploratory.txt"))
    a = ap.parse_args()
    errors = {r["id"]: r for r in read(os.path.join(ROOT, "conditions", "results", "error_conditions.csv"))}
    docs = {r["id"]: r for r in read(os.path.join(ROOT, "conditions", "results", "documentation.csv"))}
    retr = {(r["id"], r["level"]): r for r in read(os.path.join(ROOT, "conditions", "results", "retrieval.csv"))}
    cases = {r["id"]: r for r in read(os.path.join(ROOT, "test_cases", "list.csv"))}
    ids = sorted(errors, key=lambda c: (c[0] == "N", c))
    interp = [i for i in ids if "Did you mean" in errors[i]["E0"]]
    libhint = [i for i in ids if errors[i]["E0"] != errors[i]["E2"] and i not in interp]
    names_fix = [i for i in ids if docs[i]["entry_names_fix"] == "yes"]
    warning_only = [i for i in ids if docs[i]["entry_names_fix"] == "no"]
    data = {m: load(m) for m in MODELS}
    L = ["Exploratory and descriptive analyses of the main runs (Section 4.6). Percentage points, mean of the",
         f"within-change differences with a 95% cluster-bootstrap interval (seed {SEED}); n = changes.", ""]

    L.append(f"1. E0 vs E2 without documentation: {len(libhint)} changes with a library hint, "
             f"{len(interp)} with an interpreter suggestion")
    for m in MODELS:
        L.append(f"  {NAMES[m]:17} library hint {fmt(diff(data[m][0], libhint, 'E0D0', 'E2D0'))}")
    L.append("  interpreter suggestion, change by change (E0·D0 and E2·D0 correct of 5; suggestion):")
    for i in interp:
        sug = errors[i]["E0"].rsplit("Did you mean:", 1)[1].strip()
        vals = "  ".join(f"{NAMES[m].split()[0]} {sum(data[m][0][(i, 'E0D0')])}/{sum(data[m][0][(i, 'E2D0')])}"
                         for m in MODELS)
        L.append(f"    {i} {sug:22} {vals}")
    L.append("")
    L.append("2. E1 vs E2 without documentation")
    for m in MODELS:
        L.append(f"  {NAMES[m]:17} {fmt(diff(data[m][0], ids, 'E1D0', 'E2D0'))}")
    L.append("")
    L.append(f"3. D1 vs D2 by error level: entry names the fix ({len(names_fix)}) | only the old warning does "
             f"({len(warning_only)})")
    for lv in ["E0", "E1", "E2", "E3", "E4"]:
        rec_a = sum(retr[(i, lv)]["recall_at_3"] == "yes" for i in names_fix)
        rec_b = sum(retr[(i, lv)]["recall_at_3"] == "yes" for i in warning_only)
        L.append(f"  {lv}: recall@3 {rec_a}/{len(names_fix)} | {rec_b}/{len(warning_only)}")
        for m in MODELS:
            L.append(f"    {NAMES[m]:17} {fmt(diff(data[m][0], names_fix, lv + 'D1', lv + 'D2'))} | "
                     f"{fmt(diff(data[m][0], warning_only, lv + 'D1', lv + 'D2'))}")
    L.append("")
    L.append("4. D3 vs D2 by error level")
    for lv in ["E0", "E1", "E2", "E3", "E4"]:
        L.append(f"  {lv}: " + "  ".join(f"{NAMES[m].split()[0]} {fmt(diff(data[m][0], ids, lv + 'D3', lv + 'D2'))}"
                                         for m in MODELS))
    L.append("")
    L.append("5. Failures without documentation (distinct samples of 450): fails the test / fails only the "
             "validity checks / no code block")
    for lv in ["E0", "E4"]:
        for m in MODELS:
            out = [o for i in ids for o in data[m][1][(i, lv + "D0")]]
            L.append(f"  {lv}·D0 {NAMES[m]:17} {out.count('fails the test'):3d} / "
                     f"{out.count('fails the validity checks'):2d} / {out.count('no code block'):2d}")
    L.append("")
    L.append("6. pass@1 (%) of the primary conditions by library and by type of change")
    groups = {"pandas": [i for i in ids if cases[i]["library"] == "pandas"],
              "NumPy": [i for i in ids if cases[i]["library"] == "NumPy"]}
    for t in ("removed API", "removed parameter", "behavior change (raises)"):
        groups[t] = [i for i in ids if cases[i]["change_type"] == t]
    conds = ["E0D0", "E2D0", "E3D0", "E4D0", "E2D2", "E3D2", "E4D2"]
    L.append("  " + " " * 48 + "  ".join(f"{c:>5}" for c in conds))
    for m in MODELS:
        for g, gids in groups.items():
            vals = [100 * np.mean([np.mean(data[m][0][(i, c)]) for i in gids]) for c in conds]
            L.append(f"  {NAMES[m]:17} {g:24} ({len(gids):2d})  " + "  ".join(f"{v:5.1f}" for v in vals))
    text = "\n".join(L) + "\n"
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(text, end="")


if __name__ == "__main__":
    main()
