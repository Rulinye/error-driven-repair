"""Template sensitivity (Section 3.6) and replication on the second test cases (Section 4.6).

usage: python analysis/sensitivity.py [--out analysis/sensitivity.txt]

Template: on the 18 test cases of the paraphrased template (runs/run.py, PARAPHRASE_SEED), the five primary
contrasts are computed under the main template (runs/results/<model>/) and the paraphrased one
(runs/results/<model>-paraphrase/). A contrast is flagged as sensitive to the template if its estimate has a
different sign under the two templates (an estimate of exactly zero has no sign and is not flagged).

Replication: on the 30 changes of the replication subset, the five primary contrasts are computed on the second
test cases (runs/results/<model>-second/) and on the first test cases of the same changes.

Percentage points; 95% cluster-bootstrap interval over the test cases (seed 20261102); no tests.
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
CONTRASTS = {"C1": {"E3D0": 1, "E2D0": -1}, "C2": {"E4D0": 1, "E2D0": -1}, "C3": {"E2D2": 1, "E2D0": -1},
             "C4": {"E2D2": 1, "E2D0": -1, "E3D2": -1, "E3D0": 1}, "C5": {"E4D2": 1, "E4D0": -1, "E2D2": -1, "E2D0": 1}}
PRIMARY = ["E2D0", "E3D0", "E4D0", "E2D2", "E3D2", "E4D2"]
SEED = 20261102


def counts_of(folder, template):
    out = {}
    with open(os.path.join(RESULTS, folder, "samples.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["template"] == template and r["condition"] in PRIMARY:
                key = (r["case"], r["condition"])
                out[key] = out.get(key, 0) + (r["correct"] == "True")
    return out


def estimate(data, ids, weights):
    d = 20 * np.array([sum(w * data[(i, k)] for k, w in weights.items()) for i in ids], dtype=float)
    low, high = np.percentile(resampled_means(d[:, None], counts(len(ids), seed=SEED))[:, 0], [2.5, 97.5])
    return d.mean(), low, high


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "sensitivity.txt"))
    a = ap.parse_args()
    L = ["Template sensitivity and replication. Percentage points; 95% cluster-bootstrap interval "
         f"(seed {SEED}).", ""]
    para_ids = None
    L.append("Paraphrased template: the five primary contrasts on its test cases, main | paraphrased template")
    flagged = []
    for m in MODELS:
        main_t = counts_of(m, "main")
        para = counts_of(f"{m}-paraphrase", "paraphrase")
        ids = sorted({c for c, _ in para}, key=lambda c: (c[0] == "N", c))
        para_ids = para_ids or ids
        assert ids == para_ids and len(ids) == 18
        L.append(f"  {NAMES[m]}")
        for name, w in CONTRASTS.items():
            em, lm, hm = estimate(main_t, ids, w)
            ep, lp, hp = estimate(para, ids, w)
            flag = em * ep < 0
            flagged += [(m, name)] if flag else []
            L.append(f"    {name}  {em:+6.1f} [{lm:+6.1f}, {hm:+6.1f}] | {ep:+6.1f} [{lp:+6.1f}, {hp:+6.1f}]"
                     f"{'   SENSITIVE (sign differs)' if flag else ''}")
    L.append(f"  test cases: {' '.join(para_ids)}")
    L.append(f"  contrasts with a different sign under the two templates: "
             f"{', '.join(f'{NAMES[m]} {c}' for m, c in flagged) or 'none'}")
    L.append("")
    L.append("Replication: the five primary contrasts on the 30 changes of the subset, first | second test cases")
    for m in MODELS:
        first = counts_of(m, "main")
        second = counts_of(f"{m}-second", "main")
        sids = sorted({c for c, _ in second}, key=lambda c: (c[0] == "N", c))
        assert len(sids) == 30
        fids = [c[:-1] for c in sids]
        L.append(f"  {NAMES[m]}")
        for name, w in CONTRASTS.items():
            ef, lf, hf = estimate(first, fids, w)
            es, ls, hs = estimate(second, sids, w)
            L.append(f"    {name}  {ef:+6.1f} [{lf:+6.1f}, {hf:+6.1f}] | {es:+6.1f} [{ls:+6.1f}, {hs:+6.1f}]")
        base_f = 20 * np.mean([first[(i, "E2D0")] for i in fids])
        base_s = 20 * np.mean([second[(i, "E2D0")] for i in sids])
        L.append(f"    E2·D0 success {base_f:5.1f} | {base_s:5.1f}")
    text = "\n".join(L) + "\n"
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(text, end="")


if __name__ == "__main__":
    main()
