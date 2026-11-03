# Measurements

This folder builds the Python environments of the study and reruns every number in the first thesis
draft (October 18, 2026) that was measured, as opposed to cited, and compares each one with the number
written in that draft.

## Which chapters contain measurements

| chapter | measured numbers | note |
| --- | --- | --- |
| 1 Introduction | two | entries in the pandas 2.0.0 release notes (233); Ruff fixes 3 of 9 pilot cases (from Chapter 5) |
| 2 Related work | none | all numbers are cited from other papers |
| 3 Study design | yes | the candidate changes, hint statistics, templates and suggestions |
| 4 Analysis plan | none | plan only |
| 5 Pilot study | yes | the 9 pilot cases, Ruff, interpreter suggestions |
| 6 Results | none | the repair experiment has not been run yet |
| 7 Threats to validity | none in that draft | error messages under Python 3.13 are measured as well |
| 8 Work plan | none | plan only |

## What is reproduced

| content | section | script |
| --- | --- | --- |
| 233 entries under "Removal of prior version deprecations/changes" in the pandas 2.0.0 release notes | 1 | `scripts/count_release_notes.py` |
| pilot: 9 cases pass the four execution checks; 3 wrong fixes are caught | 5.2, 5.3 | `scripts/pilot.py` |
| Ruff 0.16.10 on the pilot cases (detects 4, fixes 3) | 1, 5.5 | `scripts/ruff_pilot.py` |
| minimal calls of the 100 candidate changes: 93 raise, 5 silent, 2 same; error messages; replacement check | 3.2.2, Table 1 | `scripts/candidates.py`, `scripts/candidates_spec.py` |
| hint statistics: 23/48, 30/52, pandas 1/47, NumPy 29/35 | 3.3, 5.3, Table 4 | `scripts/summarize.py` |
| "Did you mean" suggestions for the 54 attribute errors under Python 3.11 (9) | 5.4 | `scripts/probe_suggestions.py` |
| the three library combinations run under Python 3.11; a fix with `_append` passes the test; the E4 suggestion `apply` fails | 3.2.1, 3.9, Table 2 | `scripts/extra_checks.py` |
| the 82 error messages under Python 3.13: 7 differ from 3.11; 5 new keyword-name suggestions, of which 3 lead to a correct fix, 1 fails and 1 gives a wrong result | 7 (to be added) | `scripts/py313_messages.py` |

The comparison of the public APIs in Section 3.2.2 is in `screening/`.
The Python 3.13 measurement above uses the minimal calls of the 82 changes of the first draft. For the 90 test
cases of the current draft, `conditions/py313.py` runs their programs and finds the same 7 differences.

## How to run (macOS or Linux)

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) once:
   `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. From the repository root:
   `cd measurements && bash run_all.sh`
   The first run downloads Python 3.11 and 3.13 and the library versions (several minutes);
   later runs take a few minutes.
3. Open `results/summary.md`. The first line should read "42 of 42 items match the draft". The
   three items marked "7 (to be added)" are the Python 3.13 measurements, which that draft did not
   yet contain.

## Environments

The first three match Section 3.2.1 of the thesis; all use Python 3.11.

| name | pandas | NumPy | used for |
| --- | --- | --- | --- |
| `envs/old` | 1.5.3 | 1.23.5 | old environment of the pandas study |
| `envs/mid` | 2.2.3 | 1.23.5 | new environment of the pandas study and old environment of the NumPy study |
| `envs/new` | 2.2.3 | 2.1.3 | new environment of the NumPy study |
| `envs/py313` | 2.2.3 | 2.1.3 | Python 3.13, only for the Chapter 7 measurements |
| `envs/tools` | – | – | runs the scripts (Ruff 0.16.10) |

`envs/` is not committed; `run_all.sh` rebuilds it from the pinned, hashed requirements in
`requirements/` (one file per environment, all dependencies included). To rebuild an existing
environment from these files, delete its folder under `envs/` and run `run_all.sh` again.

## Results

`results/` holds the raw records of a run (`release_notes.json`, `pilot.json`, `ruff.json`,
`candidates.json`, `suggestions.json`, `extra.json`, `py313.json`) and the comparison table
`summary.md`. They are committed, so each number in the draft has a dated source.

## Notes

1. **Decisions are recorded, not recomputed.** Which changes were selected and why is recorded in
   `data/changes.csv` (see `data/README.md`). The scripts read these decisions; they do not make them.
2. **The minimal calls were rewritten.** The script used during the original screening was not
   kept; `scripts/candidates_spec.py` was written again from the change list. Its results agree
   with the recorded ones for all 100 classifications and all 93 error messages.
3. **Python 3.11 throughout.** The draft states that the pilot used Python 3.10 (old) and 3.12
   (new). Here everything runs under Python 3.11, as in the main study, with the same results.
4. **Two replacements that need care:**
   - **P50 (`astype('datetime64[D]')`):** pandas 1.5.3 ignored the `[D]` unit and kept the time,
     so `s.dt.floor('D')` is equivalent only for times at midnight. The equivalent replacement is
     `astype('datetime64[s]')`, which the scripts use.
   - **P35 (`loffset`):** the release-note entry says "Use offset or origin instead", but that
     advice refers to `base`. The equivalent replacement for `loffset` is to shift the index after
     resampling, as the old deprecation warning says; the scripts do this.
5. **Paths in error messages** (for example the site-packages path in P55) are replaced by
   `<site-packages path>`, because they differ between computers.
6. `data/pandas_v2.0.0_whatsnew.rst` is a copy of `doc/source/whatsnew/v2.0.0.rst` from the pandas
   repository, saved on October 18, 2026.
