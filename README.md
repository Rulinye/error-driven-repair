# Error-Driven Code Repair for Python Library Upgrades

Bachelor's thesis of Ding Cheng (20221480), School of Software, Chung-Ang University, 2026.

The thesis measures how much the runtime error message, compared with migration documentation,
helps a large language model repair Python code broken by two library upgrades:
pandas 1.5.3 → 2.2.3 and NumPy 1.23.5 → 2.1.3.

## Folders

| folder | content |
| --- | --- |
| `measurements/` | builds the Python environments of the study and reruns every number measured in the first draft of October 18, 2026: `bash measurements/run_all.sh` |
| `screening/` | the candidate pool for the test cases: API comparison, release notes, selection criteria, random draw |
| `test_cases/` | the 90 test cases (old program, test, reference fix) and their admission checks |
| `conditions/` | the error conditions (E0–E4) and the documentation conditions (D0–D3) for every test case |
| `probe/` | the knowledge probe: the questions, the answers of the four models and their labels |
| `runs/` | the prompts, the model calls and the judging of the fixes; the dry runs |
| `analysis/` | confidence intervals, p-values and Holm's procedure; the power simulation |
| `examples/multi-change-example/` | the example of Chapter 1: one pandas 1.x script that crashes five times after the upgrade |
| `thesis/` | the thesis draft (Word) |

## Status

The hypotheses and the analysis plan (Chapter 4 of the draft in `thesis/`) were frozen before any main run,
at the commit tagged `plan-frozen`.
