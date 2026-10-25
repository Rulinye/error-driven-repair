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

The programs and test scripts of the test cases will be added to this folder.
