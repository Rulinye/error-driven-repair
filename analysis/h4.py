"""H4: the effect of a correct hint (C1) and of correct documentation (C3) on the changes a model does not know
(Section 4.4), with the two sensitivity analyses of the probe labels and the descriptive split by stratum.

usage: python analysis/h4.py [--out analysis/h4.txt]

The unknown stratum of a model is the real changes that the knowledge probe labels unknown
(probe/results/known.csv) together with the synthetic changes it does not answer correctly
(synthetic/results/known.csv). C1 (E3·D0 - E2·D0) and C3 (E2·D2 - E2·D0) are computed within each change and
averaged over the stratum, with the bootstrap interval and the sign-flip p-value of inference.py; the two
p-values of a model are adjusted with Holm's procedure. H4 is supported for a contrast if it is significant in
the predicted direction (> 0) for at least three of the four models.

Sensitivity (Section 4.4): the same test with the threshold for a known change set to two and to four of the
five answers instead of three, and with the labels taken from the automatic matches alone (the 12 real changes
labelled entirely by hand keep their hand labels; the synthetic answers have no hand labels unless
synthetic/results/hand_labels.csv gives them). Only whether the conclusion on H4 changes is reported.

Descriptive (Section 4.6): the five primary contrasts in the known and the unknown stratum of each model, the
real and the synthetic unknown changes apart, and the success under E2·D0 by stratum as a check of the labels.
"""
import argparse
import csv
import os
import sys
from collections import defaultdict

import numpy as np

from inference import contrast, counts, holm, signs

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
RESULTS = os.path.join(ROOT, "runs", "results")
sys.path.insert(0, os.path.join(ROOT, "probe"))
from questions import REVIEW  # noqa: E402

MODELS = ["gpt-6-luna", "gemini-3.8-flash", "qwen2.5-coder-7b", "codellama-7b"]
NAMES = {"gpt-6-luna": "GPT-6 Luna", "gemini-3.8-flash": "Gemini 3.8 Flash",
         "qwen2.5-coder-7b": "Qwen2.5-Coder-7B", "codellama-7b": "CodeLlama-7B"}
CONDITIONS = ["E2D0", "E3D0", "E4D0", "E2D2", "E3D2", "E4D2"]
H4 = {"C1": {"E3D0": 1, "E2D0": -1}, "C3": {"E2D2": 1, "E2D0": -1}}
ALL5 = {"C1": ({"E3D0": 1, "E2D0": -1}, +1), "C2": ({"E4D0": 1, "E2D0": -1}, -1),
        "C3": ({"E2D2": 1, "E2D0": -1}, +1), "C4": ({"E2D2": 1, "E2D0": -1, "E3D2": -1, "E3D0": 1}, +1),
        "C5": ({"E4D2": 1, "E4D0": -1, "E2D2": -1, "E2D0": 1}, +1)}
SEED = 20261102
ALPHA = 0.05


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def correct_counts(folder):
    """{case: {condition: correct samples of 5}} for the six primary conditions."""
    out = defaultdict(lambda: defaultdict(int))
    n = defaultdict(int)
    for r in read(os.path.join(RESULTS, folder, "samples.csv")):
        if r["template"] == "main" and r["condition"] in CONDITIONS:
            out[r["case"]][r["condition"]] += r["correct"] == "True"
            n[(r["case"], r["condition"])] += 1
    assert all(v == 5 for v in n.values()), folder
    return out


def answer_labels():
    """{(model, id): (labels of the five answers, automatic labels)} for the real and the synthetic changes."""
    out = defaultdict(lambda: ([], []))
    for r in read(os.path.join(ROOT, "probe", "results", "answer_labels.csv")):
        auto = (r["hand_label"] if r["id"] in REVIEW else r["auto_match"]) == "yes"
        out[(r["model"], r["id"])][0].append(r["correct"] == "yes")
        out[(r["model"], r["id"])][1].append(auto)
    for r in read(os.path.join(ROOT, "synthetic", "results", "answer_labels.csv")):
        out[(r["model"], r["id"])][0].append(r["correct"] == "yes")
        out[(r["model"], r["id"])][1].append(r["automatic"] == "yes" if not r["hand"] else r["hand"] == "yes")
    assert all(len(a) == 5 and len(b) == 5 for a, b in out.values())
    return out


def unknown(labels, model, ids, threshold=3, automatic=False):
    return [cid for cid in ids if sum(labels[(model, cid)][1 if automatic else 0]) < threshold]


def diffs(data, ids, weights):
    return 20 * np.array([sum(w * data[cid][k] for k, w in weights.items()) for cid in ids], dtype=float)


def test_h4(data, labels, ids, **kw):
    """{model: {contrast: (n, mean, low, high, p, p_holm, supported)}} and {contrast: models supported}."""
    out, support = {}, {}
    for model in MODELS:
        u = unknown(labels, model, ids, **kw)
        rows = {}
        c, s = counts(len(u), seed=SEED), signs(len(u), seed=SEED + 1)
        for name, w in H4.items():
            rows[name] = [len(u), *contrast(diffs(data[model], u, w), c, s)]
        for name, adj in zip(H4, holm([rows[k][4] for k in H4])):
            rows[name] += [adj, adj < ALPHA and rows[name][1] > 0]
        out[model] = rows
    for name in H4:
        support[name] = sum(out[m][name][6] for m in MODELS)
    return out, support


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "h4.txt"))
    a = ap.parse_args()
    data = {}
    for model in MODELS:
        d = dict(correct_counts(model))
        d.update(correct_counts(f"{model}-synthetic"))
        data[model] = d
    real = sorted(cid for cid in data[MODELS[0]] if not cid.startswith("S"))
    synthetic = sorted(cid for cid in data[MODELS[0]] if cid.startswith("S"))
    assert len(real) == 90 and len(synthetic) == 15
    ids = real + synthetic
    labels = answer_labels()

    lines = ["H4: C1 and C3 on the changes each model does not know (real changes labelled unknown by the probe",
             "and synthetic changes it does not answer correctly). Percentage points; 95% cluster-bootstrap CI;",
             f"sign-flip p-value; Holm over C1 and C3 within each model; seeds {SEED} and {SEED + 1}.", ""]
    main_res, support = test_h4(data, labels, ids)
    for model in MODELS:
        n_real = len(unknown(labels, model, real))
        n_syn = len(unknown(labels, model, synthetic))
        lines.append(f"{NAMES[model]}: {n_real} real + {n_syn} synthetic unknown changes")
        for name, (n, mean, low, high, p, adj, ok) in main_res[model].items():
            lines.append(f"  {name}  {mean:+6.1f}  [{low:+6.1f}, {high:+6.1f}]  p {p:.4f}  p (Holm) {adj:.4f}  "
                         f"{'significant, predicted direction' if ok else 'not significant'}")
    lines.append("")
    for name in H4:
        lines.append(f"H4 for {name}: {support[name]} of 4 models; rule: at least 3 of 4 -> "
                     f"{'supported' if support[name] >= 3 else 'not supported'}")
    lines.append("")
    lines.append("Sensitivity of the conclusion to the probe labels")
    for label, kw in [("threshold 2 of 5", {"threshold": 2}), ("threshold 4 of 5", {"threshold": 4}),
                      ("automatic matches alone", {"automatic": True})]:
        res, sup = test_h4(data, labels, ids, **kw)
        sizes = ", ".join(f"{NAMES[m]} {res[m]['C1'][0]}" for m in MODELS)
        verdict = "; ".join(f"{k}: {sup[k]} of 4 -> {'supported' if sup[k] >= 3 else 'not supported'}"
                            f"{'' if (sup[k] >= 3) == (support[k] >= 3) else ' (CHANGED)'}" for k in H4)
        lines.append(f"  {label}: unknown changes {sizes}")
        lines.append(f"    {verdict}")
    lines.append("")
    lines.append("Descriptive: the five contrasts by stratum (mean, percentage points; n changes); E2·D0 success")
    for model in MODELS:
        u_real = unknown(labels, model, real)
        u_syn = unknown(labels, model, synthetic)
        strata = {"known (real and synthetic)": [i for i in ids if i not in u_real + u_syn],
                  "unknown, real": u_real, "unknown, synthetic": u_syn}
        lines.append(f"  {NAMES[model]}")
        for sname, sids in strata.items():
            if not sids:
                lines.append(f"    {sname:27}  n  0")
                continue
            parts = []
            for name, (w, _) in ALL5.items():
                parts.append(f"{name} {diffs(data[model], sids, w).mean():+6.1f}")
            base = 20 * np.mean([data[model][i]["E2D0"] for i in sids])
            lines.append(f"    {sname:27}  n {len(sids):3d}  " + "  ".join(parts) + f"  E2D0 {base:5.1f}")
    text = "\n".join(lines) + "\n"
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(text, end="")


if __name__ == "__main__":
    main()
