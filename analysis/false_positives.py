"""How often each test rejects a true null hypothesis when only a few changes differ (decision for Section 4.3).

usage: python analysis/false_positives.py [--out analysis/false_positives.txt]

Of 90 changes, k are solved under one condition and not under the other, each in a random direction, and the
others are the same under both, as when the samples of a change are identical. There is no effect, so every
rejection at alpha = 0.01 or 0.05 is a false positive. The p-value read from the bootstrap distribution
(twice the smaller share of resampled means on either side of zero) is compared with the sign-flip test,
over 20,000 simulated sets per k.
"""
import argparse
import os

import numpy as np

from inference import bootstrap_p_values, counts, resampled_means, sign_flip_p_values, signs

HERE = os.path.dirname(os.path.abspath(__file__))
CHANGES = 90
SETS = 20_000
SEED = 20261102


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "false_positives.txt"))
    a = ap.parse_args()
    c, s = counts(CHANGES, seed=SEED + 1), signs(CHANGES, seed=SEED + 2)
    rng = np.random.default_rng(SEED)
    lines = [f"Share of {SETS:,} simulated sets without an effect in which the test rejects, for {CHANGES} changes",
             "of which k differ between the two conditions.", "",
             "   k   bootstrap 0.01   sign-flip 0.01   bootstrap 0.05   sign-flip 0.05"]
    for k in (4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 30, 45, 90):
        d = np.zeros((CHANGES, SETS), dtype=np.float32)
        d[:k] = np.where(rng.random((k, SETS)) < 0.5, -1.0, 1.0)
        boot, flip = bootstrap_p_values(resampled_means(d, c)), sign_flip_p_values(d, s)
        lines.append(f"  {k:2}   {np.mean(boot < 0.01):14.4f}   {np.mean(flip < 0.01):14.4f}   "
                     f"{np.mean(boot < 0.05):14.4f}   {np.mean(flip < 0.05):14.4f}")
    text = "\n".join(lines)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
