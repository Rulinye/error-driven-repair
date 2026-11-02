# Analysis

Chapter 4 of the thesis. Run from the repository root, after the runs of `runs/`.

```bash
python analysis/false_positives.py   # false positives of the two tests when few changes differ -> false_positives.txt
python analysis/power.py             # minimum detectable effects from the dry runs (Section 4.5) -> power.txt
```

## Intervals, p-values and Holm (`inference.py`)

A contrast is computed within each change and then averaged over the changes (Section 4.3).

- **Confidence interval:** cluster bootstrap over changes, 10,000 resamples of whole changes; the 95% interval
  is the middle 95% of the resampled means.
- **p-value:** sign-flip test. The sign of every within-change difference is flipped at random, 10,000 times;
  the two-sided p-value is the share of sign assignments, the observed one included, whose mean is at least
  as far from zero as the observed mean.
- **Holm's procedure** adjusts the p-values of the five contrasts within a model (Section 4.4).

The p-value was first to be read from the bootstrap distribution (twice the smaller share of resampled means
on either side of zero). At temperature 0.2 the five samples of a change are often identical, so two
conditions often differ on only a few changes, and then that p-value is too small (`false_positives.txt`):
when 6 of 90 changes differ, all by chance in the same direction, it is below 0.01, although the chance of
this is 2 / 2^6 = 3.1%; over 20,000 simulated sets without an effect it rejects in up to 3.1% at alpha = 0.01
and up to 12.4% at alpha = 0.05. The sign-flip test never exceeds alpha.

## Power (`power.py`, `power.txt`)

For each model, a binomial mixed model with an effect for the change and one for the change under the
condition is fitted to the dry run, with the mean success rate of every primary condition set to its dry-run
rate. Data for 90 changes are simulated from it; an effect is created in one condition (see the docstring for
each contrast), and the minimum detectable effect is the size at which the sign-flip test detects it in the
predicted direction at alpha = 0.01 in 80% of the simulated data sets.

Where a model already solves the base condition of a contrast almost always, the success rate has no room
to rise, and the contrast cannot be detected at any size; `power.txt` then gives the largest possible effect
and its power.
