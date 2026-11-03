# Analysis

Chapter 4 of the thesis. Run from the repository root, after the runs of `runs/`.

```bash
python analysis/false_positives.py   # false positives of the two tests when few changes differ -> false_positives.txt
python analysis/power.py             # minimum detectable effects from the dry runs (Section 4.5) -> power.txt
python analysis/primary.py           # the five primary contrasts and overall support (Section 4.4) -> primary.txt
Rscript analysis/logit_check.R > analysis/logit_check.txt   # logit-scale check of C4 and C5 (Section 4.3)
python analysis/ruff_baseline.py     # Ruff on the 90 test cases, judged like a model's fix (RQ1) -> ruff.csv, ruff.txt
python analysis/h4.py                # H4 on the unknown changes, with the sensitivity of the probe labels -> h4.txt
python analysis/sensitivity.py       # template sensitivity and replication on the second test cases -> sensitivity.txt
python analysis/exploratory.py       # the exploratory and descriptive analyses of Section 4.6 -> exploratory.txt
python analysis/synthetic.py         # pass@1 under all 20 conditions and C1–C5 on the synthetic changes -> synthetic.txt
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

## Primary contrasts (`primary.py`, `primary.txt`)

The success rate of a change under a condition is the share of its five samples that are correct
(`runs/results/<model>/samples.csv`, main template). C1 to C5 are computed within each change and averaged
over the 90 changes, in percentage points, with the bootstrap interval and the sign-flip p-value of
`inference.py` (seeds 20261102 and 20261103) and Holm's procedure within each model. A contrast counts if its
adjusted p-value is below 0.05 and its mean has the predicted sign. H1 and H3a–H3c are supported overall if
their contrast counts for both open models, and H2 if it counts for at least three of the four models
(Section 4.4). For the commercial models, C1 and C3–C5 are printed with the largest increase that the base
condition allows (100 minus the rate of E2·D0, or of E4·D0 for C5), as in `power.py`.

## Logit-scale check (`logit_check.R`, `logit_check.txt`)

For each model, `glmer(cbind(correct, 5 - correct) ~ E * D + (1 | change) + (1 | change:condition),
family = binomial)` on the six primary conditions, with lme4's defaults (R 4.3.3, lme4 1.1-35.1). With E2 and
D0 as reference levels, C4 on the logit scale is minus the coefficient of E3:D2 and C5 is the coefficient of
E4:D2. An interaction whose sign differs between the two scales is reported as dependent on the scale
(Section 4.3). Warnings of the fit, such as a failure to converge, are printed with each model.

## Rule-based baseline (`ruff_baseline.py`, `ruff.csv`, `ruff.txt`)

Ruff 0.16.10 (`measurements/envs/tools`) with the rules NPY001, NPY003, NPY201 and PD, first to report and then
with its safe automatic fixes, on the old program of every test case (Section 3.10). The fixed program is judged
by `runs/score.py` like a model's fix. `ruff.txt` puts the share that Ruff fixes next to pass@1 under E0·D0 of
every model (RQ1).
