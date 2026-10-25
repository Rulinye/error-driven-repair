# Reproduced numbers compared with the thesis draft

42 of 42 items match the draft; 0 differ.

Environments: old (pandas 1.5.3 + NumPy 1.23.5): Python 3.11.17, pandas 1.5.3, NumPy 1.23.5; mid (pandas 2.2.3 + NumPy 1.23.5): Python 3.11.17, pandas 2.2.3, NumPy 1.23.5; new (pandas 2.2.3 + NumPy 2.1.3): Python 3.11.17, pandas 2.2.3, NumPy 2.1.3

| Draft section | Item | Draft | This run | Match |
| --- | --- | --- | --- | --- |
| 1 | pandas 2.0.0 release notes: entries under 'Removal of prior version deprecations/changes' | 233 | 233 | yes |
| 3.2.2, Table 1 | candidate changes | 100 | 100 | yes |
| 3.2.2, Table 1 | raise an error (pandas / NumPy / total) | 55 / 38 / 93 | 55 / 38 / 93 | yes |
| 3.2.2, Table 1 | change results silently (pandas / NumPy / total) | 4 / 1 / 5 | 4 / 1 / 5 | yes |
| 3.2.2, Table 1 | behave the same (pandas / NumPy / total) | 1 / 1 / 2 | 1 / 1 / 2 | yes |
| 3.2.2 | candidates classified as recorded in changes.csv | 100 | 100 | yes |
| 3.2.2 | error messages identical to the recorded ones (first 60 characters) | 93 | 93 | yes |
| 3.2.2 | selected changes (pandas / NumPy / total) | 46 / 29 / 75 | 46 / 29 / 75 | yes |
| 3.2.2 | selected changes by type (removed API / removed parameter / behavior change / silent) | 46 / 19 / 6 / 4 | 46 / 19 / 6 / 4 | yes |
| 3.2.2 | the 86 planned changes by type (removed API / removed parameter / behavior change / silent) | 55 / 21 / 6 / 4 | 55 / 21 / 6 / 4 | yes |
| 3.2.2 | selected 75: replacement gives the same values as the old call | 75 | 75 | yes |
| 3.2.2 | re-admitted 11: replacement gives the same values as the old call | 11 | 11 | yes |
| 3.3 | selected changes that raise an error | 71 | 71 | yes |
| 3.3 | of these 71: with hint / without hint | 23 / 48 | 23 / 48 | yes |
| 3.3 | hint rule agrees with the recorded label | 71 / 71 | 71 / 71 | yes |
| 3.3 | re-admitted 11: NumPy with hint / pandas with hint | 7 of 7 / 0 of 4 | 7 of 7 / 0 of 4 | yes |
| 3.3, Table 4 | of the 82: with hint / without hint | 30 / 52 | 30 / 52 | yes |
| 5.3, Table 4 | pandas: with hint / erroring changes | 1 / 47 | 1 / 47 | yes |
| 5.3, Table 4 | NumPy: with hint / erroring changes | 29 / 35 | 29 / 35 | yes |
| 5.3 | of the 71: pandas 1/43, NumPy 22/28 | 1/43, 22/28 | 1/43, 22/28 | yes |
| 5.3 | removed parameters: with hint / total | 0 / 21 | 0 / 21 | yes |
| 5.4 | attribute errors | 54 | 54 | yes |
| 5.4 | with a 'Did you mean' suggestion | 9 | 9 | yes |
| 5.4 | suggestions | N15 cumprod, P01 _append, P02 _append, P03 isetitem, P09 _join_monotonic, P14 _mode, P26 map, P27 map, P28 shift | N15 cumprod, P01 _append, P02 _append, P03 isetitem, P09 _join_monotonic, P14 _mode, P26 map, P27 map, P28 shift | yes |
| 3.4 | changes whose E0 equals E2 (no library hint, no interpreter suggestion) | 43 | 43 | yes |
| 3.4 / 3.7 | NumPy changes whose E0 already has the E3 template form (about 20) | 20 | 20 | yes |
| 3.5 | 13 pandas changes whose release-note entry names no fix: old version warns | 13 | 13 | yes |
| 5.2 | pilot cases passing all four checks | 9 / 9 | 9 / 9 | yes |
| 5.2 | wrong fixes caught by the test | 3 / 3 | 3 / 3 | yes |
| 5.3 | pilot cases that raise / with hint (NumPy only?) | 8 / 3 (NumPy only) | 8 / 3 (NumPy only) | yes |
| 5.4 | pilot pandas errors with 'Did you mean' | 2 / 4 | 2 / 4 | yes |
| 5.5 | Ruff version | ruff 0.16.10 | ruff 0.16.10 | yes |
| 5.5 | Ruff detected / fixed | 4 / 3 | 4 / 3 | yes |
| 5.5 | cases fixed by Ruff | C5, C6, C7 | C5, C6, C7 | yes |
| 5.5 | pandas cases detected by Ruff | 0 | 0 | yes |
| 3.2.1 | all three library combinations run under Python 3.11 | True | True | yes |
| 3.9 / 5.4 | a fix calling the private _append passes the pilot test | True | True | yes |
| Table 2 | a fix following the E4 suggestion 'apply' passes the pilot test | False | False | yes |
| 5.4 | keyword and import errors carry no 'Did you mean' (Python 3.11) | True | True | yes |
| 7 (to be added) | of the 82 error messages, different under Python 3.13 | 7 | 7 | yes |
| 7 (to be added) | new keyword-name suggestions under Python 3.13 | 5 | 5 | yes |
| 7 (to be added) | following them: correct / fails / wrong result | 3 / 1 / 1 | 3 / 1 / 1 | yes |
