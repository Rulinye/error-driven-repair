# Error-Driven Code Repair for Python Library Upgrades

Bachelor's thesis of Ding Cheng (20221480), School of Software, Chung-Ang University, 2026.

The thesis measures how much the runtime error message, compared with migration documentation,
helps a large language model repair Python code broken by two library upgrades:
pandas 1.5.3 → 2.2.3 and NumPy 1.23.5 → 2.1.3.

## Folders

| folder | content |
| --- | --- |
| `measurements/` | reruns every number measured so far (Chapters 1, 3, 5 and 7) and compares it with the draft: `bash measurements/run_all.sh` |
| `screening/` | the candidate pool for the test cases: API comparison, release notes, selection criteria, random draw |
| `test_cases/` | the list of the 90 test cases |
| `conditions/` | the error conditions (E0–E4) and the documentation conditions (D0–D3) for every test case |
| `probe/` | the knowledge probe: one question per test case and the scoring of the answers |
| `examples/multi-change-example/` | the example of Chapter 1: one pandas 1.x script that crashes five times after the upgrade |
| `thesis/` | the thesis draft (Word) |

The programs and tests of the test cases, the experiment harness and the analysis will be added in their own folders.

## Status

The hypotheses and the analysis plan will be frozen on October 28, 2026 (git tag `plan-frozen`).
