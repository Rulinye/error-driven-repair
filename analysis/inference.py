"""Confidence intervals, p-values and Holm's procedure for the contrasts (Sections 4.3 and 4.4).

A contrast is first computed within each change; the functions take these within-change differences.

Confidence interval: cluster bootstrap over changes. Whole changes are drawn with replacement, as many as
there are, and the mean is recomputed, RESAMPLES times; the 95% interval is the middle 95% of the resampled
means. The resampling uses a matrix of counts (how often each change is drawn in each resample), so that
the resampled means of many sets of differences are one matrix product.

p-value: sign-flip test. If the two conditions of a contrast are exchangeable within each change, every
within-change difference is as likely to have the opposite sign. The signs are flipped at random, RESAMPLES
times, and the two-sided p-value is the share of sign assignments, the observed one included, whose mean is
at least as far from zero as the observed mean. Unlike a p-value read from the bootstrap distribution, it
keeps its level when only a few changes differ between the two conditions, which is common here because
the samples of a change at temperature 0.2 are often identical.
"""
import numpy as np

RESAMPLES = 10_000


def counts(n, resamples=RESAMPLES, seed=None):
    """A resamples x n matrix: how often each of the n changes is drawn in each bootstrap resample."""
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, n, size=(resamples, n))
    c = np.zeros((resamples, n), dtype=np.float32)
    np.add.at(c, (np.arange(resamples)[:, None], draws), 1)
    return c


def signs(n, resamples=RESAMPLES, seed=None):
    """A resamples x n matrix of random signs, for the sign-flip test."""
    rng = np.random.default_rng(seed)
    return np.where(rng.random((resamples, n)) < 0.5, -1.0, 1.0).astype(np.float32)


def resampled_means(d, c):
    """Bootstrap means of the within-change differences d (changes x sets), for the counts c."""
    d = np.asarray(d, dtype=np.float32)
    return c @ d / d.shape[0]


def bootstrap_p_values(means):
    """Two-sided p-values read from bootstrap means (resamples x sets): twice the smaller share on either
    side of zero. Not used for the contrasts; kept for the comparison in false_positives.py."""
    return np.minimum(1.0, 2 * np.minimum((means <= 0).mean(axis=0), (means >= 0).mean(axis=0)))


def sign_flip_p_values(d, s):
    """Two-sided p-values of the sign-flip test for the within-change differences d (changes x sets)."""
    d = np.asarray(d, dtype=np.float32)
    observed = np.abs(d.mean(axis=0))
    flipped = np.abs(s @ d / d.shape[0])
    return (1 + (flipped >= observed - 1e-6).sum(axis=0)) / (1 + s.shape[0])


def contrast(d, c, s):
    """Mean, 95% bootstrap confidence interval and sign-flip p-value of one set of within-change differences."""
    d = np.asarray(d, dtype=float)
    low, high = np.percentile(resampled_means(d[:, None], c)[:, 0], [2.5, 97.5])
    return d.mean(), low, high, float(sign_flip_p_values(d[:, None], s)[0])


def holm(p):
    """Holm-adjusted p-values, in the order given."""
    p = np.asarray(p, dtype=float)
    adjusted = np.empty_like(p)
    running = 0.0
    for rank, i in enumerate(np.argsort(p)):
        running = max(running, (len(p) - rank) * p[i])
        adjusted[i] = min(1.0, running)
    return adjusted
