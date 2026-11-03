"""Primary contrasts of the main runs (Sections 4.3 and 4.4).

usage: python analysis/primary.py [--out analysis/primary.txt]

For each model, the success rate of a change under a condition is the share of its five samples that are
correct (runs/results/<model>/samples.csv, main template). Every contrast is computed within each change
and then averaged over the 90 changes, in percentage points:

  C1 (H1)   E3·D0 - E2·D0                          predicted > 0
  C2 (H2)   E4·D0 - E2·D0                          predicted < 0
  C3 (H3a)  E2·D2 - E2·D0                          predicted > 0
  C4 (H3b)  (E2·D2 - E2·D0) - (E3·D2 - E3·D0)      predicted > 0
  C5 (H3c)  (E4·D2 - E4·D0) - (E2·D2 - E2·D0)      predicted > 0

The 95% confidence interval comes from the cluster bootstrap and the two-sided p-value from the sign-flip
test, 10,000 resamples each with fixed seeds (analysis/inference.py). The five p-values of a model are
adjusted with Holm's procedure; a contrast is significant in the predicted direction if its adjusted p-value
is below 0.05 and its mean has the predicted sign.

Overall support (Section 4.4): H1 and H3a-H3c if their contrast is significant in the predicted direction for
both open models; H2 if it is for at least three of the four models. For the commercial models, C1 and C3-C5
are reported with the largest increase that the base condition allows: 100 minus its success rate (E2·D0 for
C1, C3 and C4; E4·D0 for C5), as in the power analysis (analysis/power.py).
"""
import argparse
import csv
import os
from collections import defaultdict

import numpy as np

from inference import contrast, counts, holm, signs

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "runs", "results")
MODELS = ["gpt-6-luna", "gemini-3.8-flash", "qwen2.5-coder-7b", "codellama-7b"]
OPEN = ["qwen2.5-coder-7b", "codellama-7b"]
COMMERCIAL = ["gpt-6-luna", "gemini-3.8-flash"]
NAMES = {"gpt-6-luna": "GPT-6 Luna", "gemini-3.8-flash": "Gemini 3.8 Flash",
         "qwen2.5-coder-7b": "Qwen2.5-Coder-7B", "codellama-7b": "CodeLlama-7B"}
CONDITIONS = ["E0D0", "E2D0", "E3D0", "E4D0", "E2D2", "E3D2", "E4D2"]
# contrast: hypothesis, weights of the conditions, predicted sign, base condition for the largest increase
CONTRASTS = {
    "C1": ("H1", {"E3D0": 1, "E2D0": -1}, +1, "E2D0"),
    "C2": ("H2", {"E4D0": 1, "E2D0": -1}, -1, None),
    "C3": ("H3a", {"E2D2": 1, "E2D0": -1}, +1, "E2D0"),
    "C4": ("H3b", {"E2D2": 1, "E2D0": -1, "E3D2": -1, "E3D0": 1}, +1, "E2D0"),
    "C5": ("H3c", {"E4D2": 1, "E4D0": -1, "E2D2": -1, "E2D0": 1}, +1, "E4D0"),
}
SEED = 20261102
ALPHA = 0.05
CHANGES = 90


def correct_counts(model):
    """{condition: {case: number of correct samples (of 5)}} for the main template. Counts are integers, so
    that the within-change differences are exact (multiples of 20 percentage points per sample)."""
    correct = defaultdict(lambda: defaultdict(list))
    with open(os.path.join(RESULTS, model, "samples.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["template"] == "main" and r["condition"] in CONDITIONS:
                correct[r["condition"]][r["case"]].append(r["correct"] == "True")
    out = {}
    for c in CONDITIONS:
        per_case = correct[c]
        assert len(per_case) == CHANGES, (model, c, len(per_case))
        assert all(len(v) == 5 for v in per_case.values()), (model, c)
        out[c] = {cid: sum(v) for cid, v in per_case.items()}
    return out


def analyse(model, c, s):
    r = correct_counts(model)
    cases = sorted(r["E2D0"])
    means = {k: 20 * np.mean([r[k][cid] for cid in cases]) for k in CONDITIONS}
    rows = []
    for name, (hyp, weights, sign, base) in CONTRASTS.items():
        d = 20 * np.array([sum(w * r[k][cid] for k, w in weights.items()) for cid in cases], dtype=float)
        mean, low, high, p = contrast(d, c, s)
        rows.append({"contrast": name, "hypothesis": hyp, "mean": mean, "low": low, "high": high, "p": p,
                     "sign": sign, "differ": int((d != 0).sum()),
                     "room": 100 - means[base] if base else None})
    for row, adj in zip(rows, holm([x["p"] for x in rows])):
        row["p_holm"] = adj
        row["supported"] = adj < ALPHA and np.sign(row["mean"]) == row["sign"]
    return means, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "primary.txt"))
    a = ap.parse_args()
    c = counts(CHANGES, seed=SEED)
    s = signs(CHANGES, seed=SEED + 1)
    lines = ["Primary contrasts of the main runs (Section 4.4): 90 changes, 5 samples per condition, main template.",
             "Rates and contrasts in percentage points; 95% cluster-bootstrap CI; two-sided sign-flip p-value;",
             f"Holm within each model; 10,000 resamples each (seeds {SEED} and {SEED + 1}).", ""]
    results = {}
    for model in MODELS:
        means, rows = analyse(model, c, s)
        results[model] = rows
        lines.append(f"{NAMES[model]}")
        lines.append("  success  " + "  ".join(f"{k}: {means[k]:5.1f}" for k in CONDITIONS))
        lines.append("  contrast  mean    95% CI            p       p (Holm)  changes that differ  "
                     "significant in predicted direction")
        for x in rows:
            extra = ""
            if model in COMMERCIAL and x["room"] is not None:
                extra = f"   (largest possible increase {x['room']:.1f})"
            lines.append(f"  {x['contrast']} ({x['hypothesis']:3})  {x['mean']:+6.1f}  [{x['low']:+6.1f}, {x['high']:+6.1f}]"
                         f"  {x['p']:.4f}  {x['p_holm']:.4f}    {x['differ']:3d}                  "
                         f"{'yes' if x['supported'] else 'no'}{extra}")
        lines.append("")
    lines.append("Overall support (Section 4.4)")
    for name, (hyp, _, _, _) in CONTRASTS.items():
        sig = {m: next(x for x in results[m] if x["contrast"] == name)["supported"] for m in MODELS}
        if hyp == "H2":
            n = sum(sig.values())
            verdict = f"{n} of 4 models; rule: at least 3 of 4 -> {'supported' if n >= 3 else 'not supported'}"
        else:
            both = all(sig[m] for m in OPEN)
            each = ", ".join(f"{NAMES[m]} " + ("yes" if sig[m] else "no") for m in OPEN)
            verdict = f"open models: {each}; rule: both -> {'supported' if both else 'not supported'}"
        lines.append(f"  {hyp:3} ({name}): {verdict}")
    text = "\n".join(lines) + "\n"
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(text, end="")


if __name__ == "__main__":
    main()
