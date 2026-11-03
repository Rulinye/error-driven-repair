"""Synthetic changes (Section 4.6): the effects of all error and documentation levels on changes that no model
can have seen.

usage: python analysis/synthetic.py [--out analysis/synthetic.txt]

For each model, pass@1 on the 15 synthetic test cases (runs/results/<model>-synthetic/) under each of the 20
conditions, and the five primary contrasts with a 95% cluster-bootstrap interval over the test cases
(seed 20261102). Percentage points; descriptive, no tests.
"""
import argparse
import csv
import os

import numpy as np

from inference import counts, resampled_means

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "runs", "results")
MODELS = ["gpt-6-luna", "gemini-3.8-flash", "qwen2.5-coder-7b", "codellama-7b"]
NAMES = {"gpt-6-luna": "GPT-6 Luna", "gemini-3.8-flash": "Gemini 3.8 Flash",
         "qwen2.5-coder-7b": "Qwen2.5-Coder-7B", "codellama-7b": "CodeLlama-7B"}
ERRORS = ["E0", "E1", "E2", "E3", "E4"]
DOCS = ["D0", "D1", "D2", "D3"]
CONTRASTS = {"C1": {"E3D0": 1, "E2D0": -1}, "C2": {"E4D0": 1, "E2D0": -1}, "C3": {"E2D2": 1, "E2D0": -1},
             "C4": {"E2D2": 1, "E2D0": -1, "E3D2": -1, "E3D0": 1}, "C5": {"E4D2": 1, "E4D0": -1, "E2D2": -1, "E2D0": 1}}
SEED = 20261102


def correct_counts(folder):
    out, samples = {}, {}
    with open(os.path.join(RESULTS, folder, "samples.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["template"] != "main":
                continue
            key = (r["case"], r["condition"])
            out[key] = out.get(key, 0) + (r["correct"] == "True")
            samples[key] = samples.get(key, 0) + 1
    return out, samples


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "synthetic.txt"))
    a = ap.parse_args()
    L = ["Synthetic changes: pass@1 under every condition and the five primary contrasts. Percentage points; "
         f"95% cluster-bootstrap interval over the test cases (seed {SEED}); descriptive, no tests.", ""]
    ids_all = None
    for m in MODELS:
        data, samples = correct_counts(f"{m}-synthetic")
        ids = sorted({c for c, _ in data})
        ids_all = ids_all or ids
        assert ids == ids_all and len(ids) == 15, (m, ids)
        conditions = [e + d for e in ERRORS for d in DOCS]
        assert all(samples.get((i, k)) == 5 for i in ids for k in conditions), m
        L.append(f"{NAMES[m]}")
        L.append("  pass@1      " + "".join(f"{d:>7}" for d in DOCS))
        for e in ERRORS:
            L.append(f"    {e}        " + "".join(f"{20 * np.mean([data[(i, e + d)] for i in ids]):7.1f}"
                                                    for d in DOCS))
        c = counts(len(ids), seed=SEED)
        for name, w in CONTRASTS.items():
            diffs = 20 * np.array([sum(v * data[(i, k)] for k, v in w.items()) for i in ids], dtype=float)
            low, high = np.percentile(resampled_means(diffs[:, None], c)[:, 0], [2.5, 97.5])
            L.append(f"  {name}  {diffs.mean():+6.1f} [{low:+6.1f}, {high:+6.1f}]")
        L.append("")
    L.append(f"test cases: {' '.join(ids_all)}")
    text = "\n".join(L) + "\n"
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(text, end="")


if __name__ == "__main__":
    main()
