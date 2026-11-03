# Test cases

`build_list.py` builds `list.csv`, the list of the changes that become test cases:

- the 82 earlier test cases (the planned changes of `measurements/data/changes.csv` that raise an
  error), except two that are not public API by the libraries' own definitions:
  - P55 `pandas.io.json.json_normalize`: the pandas API reference does not list it;
  - N31 `np.fastCopyAndTranspose`: NumPy 1.23.5 lists it as not publicly documented
    (`numpy/tests/test_public_api.py`);
- the 10 changes drawn from the candidate pool (`screening/results/draw.csv`), with the ids P61–P69
  and N41.

This gives 90 test cases (pandas 55, NumPy 35). In the candidate pool, 80 + 238 = 318 changes meet
all selection criteria; the test cases cover 90 of them.

```bash
measurements/envs/tools/bin/python test_cases/build_list.py
```

| column | meaning |
| --- | --- |
| `origin` | `earlier test case` or `drawn from the pool` |
| `pool_id` | the row of `screening/results/pool.csv` |
| `change_type`, `old_usage`, `replacement`, `changed_in`, `source` | as in `measurements/data/changes.csv` |
| `old_code`, `replacement_code` | the minimal call and its replacement (from `measurements/scripts/candidates_spec.py` or `screening/pool_spec.py`) |
| `mode` | `full` compares a Series together with its index; `values` compares values only |

## The test cases (`cases/`)

Each test case has a folder `cases/<id>/` (Section 3.2.3):

| file | content |
| --- | --- |
| `old.py` | a short program that uses the old API |
| `test.py` | the test script: imports the program as `solution`, checks the returned values and dtypes, prints `PASS` |
| `fixed.py` | the reference fix |
| `wrong.py` | a plausible wrong fix, where one exists |
| `meta.json` | the change (from `list.csv`), what the program does, and what the wrong fix does |

`check_cases.py` runs the admission checks on every folder (or on the ids given) and writes
`results/checks.csv`:

```bash
measurements/envs/tools/bin/python test_cases/check_cases.py
```

1. `old.py` passes the test in the old environment;
2. `old.py` fails in the new environment with an exception other than `AssertionError`;
3. `fixed.py` passes in the new environment;
4. `wrong.py`, if present, fails the test or fails the validity checks.

The old and new environments are those of the measurements: for pandas, pandas 1.5.3 and pandas 2.2.3
(both with NumPy 1.23.5); for NumPy, NumPy 1.23.5 and NumPy 2.1.3 (both with pandas 2.2.3). Each run has
a timeout of 60 seconds.

`check_cases.py` also scans `old.py` for the fix, as the knowledge probe matches it
(`probe/questions.py`; Section 3.2.4), and runs the static validity checks of `validity.py` on `fixed.py`
(Section 3.9): no private names from pandas or NumPy, no assignment to attributes of library objects,
and no added broad `except` clause or warning filter. For the 12 test cases whose fix is not a name
(removing an argument, assigning the result, a conversion), the scan is done by hand.

`results/checks.csv` also records the error that `old.py` raises in the new environment and the line of
`old.py` that raises it, for the error and documentation conditions.

## Second test cases (`second/`, `build_second.py`)

For the replication (Sections 3.2.3 and 4.6), 30 of the 90 changes have a second test case, written
separately in a different program context: `second/<id>b/` with the same files as `cases/<id>/`. The 30
changes were drawn on November 3, 2026, after the main runs, with `random.Random(20261104).sample` of the 90
test cases in the order of `runs/prompts.py` (pandas 20, NumPy 10):

P01 P03 P04 P11 P16 P24 P31 P32 P34 P35 P36 P37 P40 P41 P42 P45 P47 P62 P63 P64
N04 N05 N07 N10 N15 N16 N17 N22 N28 N33

```bash
measurements/envs/tools/bin/python test_cases/build_second.py
```

`build_second.py` runs the admission checks of `check_cases.py` on the second cases (all 30 admitted) and
builds their error and documentation conditions with the code of `conditions/`: E0, the failing line, E4 and
the retrieval of D1 and of the distractors of D3 come from the second program; E1, E3, D2 and the correct
chunks belong to the change and are those of the first case. The results are in `second/results/`
(`checks.csv`, `error_conditions.csv`, `documentation.csv`, `retrieval.csv`).
