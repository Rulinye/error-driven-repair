"""Minimum detectable effects of the five primary contrasts (Section 4.5).

usage: python analysis/power.py [--changes 90] [--datasets 1000] [--max-spread 30] [--out analysis/power.txt]

Model. For each model, the dry run (10 changes, the six primary conditions, 5 samples) is described by a
binomial mixed model: a sample of change i under condition k is correct with probability
logit^-1(mu_k + u_i + v_ik), with u_i ~ N(0, s_u^2) for the change and v_ik ~ N(0, s_v^2) for the change
under the condition; the second term lets a condition help some changes and not others. The mean success
rate of each condition over changes is set to its rate in the dry run, (correct + 0.5) / (samples + 1), so
that a condition without failures in the dry run gets 0.99 rather than 1; mu_k follows from it. s_u and s_v
are then estimated by maximum likelihood, integrating over the random effects on a fine grid. Most changes
of the dry run are solved in all five samples of a condition or in none, which pushes s_u up without limit
for some models; it is capped at 30 on the logit scale. With the cap, the fitted models give about the
share of conditions in which a change is solved in some but not all samples that the dry runs show (0% to
12%); a cap of 10 gives too many such cases for Qwen2.5-Coder-7B (9% against 2%).

Simulation. Data for 90 changes are drawn from the model, and each contrast is tested with the sign-flip
test of Section 4.3 (analysis/inference.py) at alpha = 0.01, the strictest Holm threshold for five
contrasts. An effect is detected if the test rejects and the mean lies in the predicted direction. The effect
is created in one condition, by changing its mean success rate by d, with the other conditions at their
dry-run rates:

  C1 (H1)   E3·D0 = E2·D0 + d, d > 0
  C2 (H2)   E4·D0 = E2·D0 + d, d < 0
  C3 (H3a)  E2·D2 = E2·D0 + d, d > 0
  C4 (H3b)  E2·D2 = E2·D0 + d, d > 0, and E3·D2 = E3·D0: documentation helps only without a hint
  C5 (H3c)  E4·D2 = E4·D0 + d, d > 0, and E2·D2 = E2·D0: documentation helps only with a misleading hint

d, in percentage points, is then the expected value of the contrast. The minimum detectable effect is the
d at which the effect is detected in 80% of the simulated data sets, found in steps of 1 point and
interpolated. Where the base condition leaves too little room (a rate cannot pass 0.999 or fall below
0.001), the largest possible d and its power are reported instead. The same random numbers are used for
every d, and all seeds are fixed.
"""
import argparse
import csv
import os

import numpy as np
from scipy.optimize import brentq, minimize
from scipy.special import expit, gammaln, logsumexp

from inference import sign_flip_p_values, signs

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "runs", "results")
MODELS = ["gpt-6-luna", "gemini-3.8-flash", "qwen2.5-coder-7b", "codellama-7b"]
CONDITIONS = ["E2D0", "E3D0", "E4D0", "E2D2", "E3D2", "E4D2"]
K = {c: i for i, c in enumerate(CONDITIONS)}
SAMPLES = 5
ALPHA = 0.01
POWER = 0.8
SEED = 20261102
MAX_SPREAD = 30.0
LOW, HIGH = 0.001, 0.999
# contrast: weights of the conditions, predicted sign, condition that is changed, its base, conditions set equal
CONTRASTS = {
    "C1 (H1)": ({"E3D0": 1, "E2D0": -1}, +1, "E3D0", "E2D0", []),
    "C2 (H2)": ({"E4D0": 1, "E2D0": -1}, -1, "E4D0", "E2D0", []),
    "C3 (H3a)": ({"E2D2": 1, "E2D0": -1}, +1, "E2D2", "E2D0", []),
    "C4 (H3b)": ({"E2D2": 1, "E2D0": -1, "E3D2": -1, "E3D0": 1}, +1, "E2D2", "E2D0", [("E3D2", "E3D0")]),
    "C5 (H3c)": ({"E4D2": 1, "E4D0": -1, "E2D2": -1, "E2D0": 1}, +1, "E4D2", "E4D0", [("E2D2", "E2D0")]),
}



def _grid(step):
    """Points and log weights of a standard normal variable on a fine grid (the probabilities change
    sharply when s_u is large, which a few quadrature nodes would miss)."""
    z = np.arange(-8, 8 + step / 2, step)
    w = np.exp(-z ** 2 / 2)
    return z, np.log(w / w.sum())


Z1, LOG_W1 = _grid(0.002)   # for mean success rates
ZU, LOG_WU = _grid(0.02)    # for the likelihood, change effect
ZV, LOG_WV = _grid(0.04)    # and change-under-condition effect


def dry_run(model):
    """Correct samples (changes x conditions) in the dry run of a model, and the change ids."""
    path = os.path.join(RESULTS, f"{model}-dryrun", "samples.csv")
    correct = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["condition"] in K:
                key = (row["case"], row["condition"])
                correct[key] = correct.get(key, 0) + (row["correct"] == "True")
    changes = sorted({c for c, _ in correct}, key=lambda c: (c[0] == "N", c))
    return np.array([[correct[(c, k)] for k in CONDITIONS] for c in changes], dtype=float), changes


def mean_rate(mu, s_u, s_v):
    """Mean success rate over changes of a condition with this mu."""
    return float(np.exp(LOG_W1) @ expit(mu + np.hypot(s_u, s_v) * Z1))


def mu_for(rate, s_u, s_v):
    return brentq(lambda m: mean_rate(m, s_u, s_v) - rate, -3000, 3000)


def log_likelihood(mu, s_u, s_v, y):
    rows, times = np.unique(y, axis=0, return_counts=True)                       # changes with the same results
    log_binom = gammaln(SAMPLES + 1) - gammaln(rows + 1) - gammaln(SAMPLES - rows + 1)
    eta = mu[:, None, None] + s_u * ZU[None, :, None] + s_v * ZV[None, None, :]    # conditions x u x v
    log_p, log_q = -np.logaddexp(0, -eta), -np.logaddexp(0, eta)
    total = 0.0
    for row, lb, n in zip(rows, log_binom, times):
        log_f = lb[:, None, None] + row[:, None, None] * log_p + (SAMPLES - row[:, None, None]) * log_q
        log_inner = logsumexp(log_f + LOG_WV[None, None, :], axis=2)              # over v
        total += n * logsumexp(log_inner.sum(axis=0) + LOG_WU)                     # over u
    return total


def fit(y):
    """Dry-run rates of the conditions, and s_u and s_v by maximum likelihood."""
    rates = (y.sum(axis=0) + 0.5) / (y.shape[0] * SAMPLES + 1)

    def spreads(t):
        return np.exp(np.clip(t, -6, np.log(MAX_SPREAD)))

    def objective(t):
        s_u, s_v = spreads(t)
        return -log_likelihood(np.array([mu_for(r, s_u, s_v) for r in rates]), s_u, s_v, y)

    best = min((minimize(objective, np.array(s, dtype=float), method="Nelder-Mead",
                         options={"xatol": 1e-4, "fatol": 1e-6})
                for s in ([0.0, -1.0], [1.0, 0.0], [2.0, 1.0], [1.5, -2.0])), key=lambda r: r.fun)
    s_u, s_v = spreads(best.x)
    return rates, float(s_u), float(s_v)


def configuration(rates, name, d):
    """Mean success rates of the six conditions with an effect d in the contrast."""
    _, _, changed, base, equal = CONTRASTS[name]
    r = rates.copy()
    for a, c in equal:
        r[K[a]] = r[K[c]]
    r[K[changed]] = r[K[base]] + d
    return r


def power(rates, s_u, s_v, name, d, noise, s):
    """Share of simulated data sets in which the contrast is detected in the predicted direction."""
    weights, sign = CONTRASTS[name][0], CONTRASTS[name][1]
    z_u, z_v, uniform = noise
    mu = np.array([mu_for(r, s_u, s_v) for r in configuration(rates, name, d)])
    p = expit(mu[None, None, :] + s_u * z_u[:, :, None] + s_v * z_v)          # data sets x changes x 6
    rate = (uniform < p[..., None]).sum(axis=-1) / SAMPLES
    w = np.zeros(len(CONDITIONS))
    for cond, v in weights.items():
        w[K[cond]] = v
    diff = rate @ w                                                          # data sets x changes
    detected = (sign_flip_p_values(diff.T, s) < ALPHA) & (np.sign(diff.mean(axis=1)) == sign)
    return float(detected.mean())


def minimum_detectable(rates, s_u, s_v, name, noise, s):
    sign, base = CONTRASTS[name][1], rates[K[CONTRASTS[name][3]]]
    room = (HIGH - base) if sign > 0 else (base - LOW)
    steps = [sign * k / 100 for k in range(1, int(room * 100) + 1)] + [sign * room]
    previous = (0.0, power(rates, s_u, s_v, name, 0.0, noise, s))
    for d in steps:
        pw = power(rates, s_u, s_v, name, d, noise, s)
        if pw >= POWER:
            d0, p0 = previous
            return 100 * (d0 + (POWER - p0) * (d - d0) / (pw - p0)), None
        previous = (d, pw)
    return None, (100 * previous[0], previous[1])


def main():
    global MAX_SPREAD
    ap = argparse.ArgumentParser()
    ap.add_argument("--changes", type=int, default=90)
    ap.add_argument("--datasets", type=int, default=1000)
    ap.add_argument("--max-spread", type=float, default=MAX_SPREAD, help="cap of s_u on the logit scale")
    ap.add_argument("--out", default=os.path.join(HERE, "power.txt"))
    a = ap.parse_args()
    MAX_SPREAD = a.max_spread

    rng = np.random.default_rng(SEED)
    noise = (rng.standard_normal((a.datasets, a.changes)),
             rng.standard_normal((a.datasets, a.changes, len(CONDITIONS))),
             rng.random((a.datasets, a.changes, len(CONDITIONS), SAMPLES)))
    s = signs(a.changes, seed=SEED + 2)
    lines = [f"Minimum detectable effects for {a.changes} changes (percentage points, in the predicted direction),",
             f"at alpha = {ALPHA} with {POWER:.0%} power; {a.datasets} simulated data sets per effect size.", ""]
    for model in MODELS:
        y, changes = dry_run(model)
        rates, s_u, s_v = fit(y)
        lines.append(f"{model}: dry run of {len(changes)} changes; s_u = {s_u:.1f} (at most {MAX_SPREAD:g}), "
                     f"s_v = {s_v:.1f}")
        lines.append("  condition       " + "  ".join(CONDITIONS))
        lines.append("  dry-run rate    " + "  ".join(f"{r:4.2f}" for r in y.sum(axis=0) / (len(changes) * SAMPLES)))
        lines.append("  rate used       " + "  ".join(f"{r:4.2f}" for r in rates))
        for name in CONTRASTS:
            mde, best = minimum_detectable(rates, s_u, s_v, name, noise, s)
            if mde is not None:
                lines.append(f"  {name:9} {mde:+5.1f}")
            else:
                lines.append(f"  {name:9} not detectable: at most {best[0]:+.1f} possible, power {best[1]:.2f}")
        null = power(rates, s_u, s_v, "C1 (H1)", 0.0, noise, s)
        lines.append(f"  check: share of data sets with C1 detected when E3·D0 = E2·D0: {null:.3f}")
        lines.append("")
    text = "\n".join(lines)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
