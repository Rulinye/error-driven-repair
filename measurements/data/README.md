# Change list

`changes.csv` lists the 100 candidate breaking changes and the decision on each:
P01–P60 for pandas 1.5.3 → 2.2.3 and N01–N40 for NumPy 1.23.5 → 2.1.3.

## Columns

| column | meaning |
| --- | --- |
| `id` | P = pandas, N = NumPy |
| `library` | pandas or NumPy |
| `old_usage` | the old code |
| `replacement` | the replacement given by the release notes or the library |
| `changed_in` | version in which the usage was removed or changed |
| `change_type` | `removed API`, `removed parameter`, `behavior change (raises)` or `silent change` |
| `observed` | the old code run in the new environment: `raises`, `silent` (runs, different result) or `same` |
| `new_error_or_change` | the error message of the new version, or the change in the result |
| `hint_in_error` | whether the error message names the fix, by the rule of Section 3.3 of the thesis: `yes` or `no` |
| `replacement_check` | the replacement run in the new environment and compared with the old result |
| `source` | release-note file and line, or migration-guide section |
| `decision` | `included` or `excluded` under the criteria of the proposal of October 6, 2026 |
| `reason` | reason for the decision |
| `note` | corrections and remarks |

## How the candidates were selected

1. **Candidates.** 100 candidates were chosen by hand from the API differences between the two
   versions and from the behavior changes described in the release notes.
2. **Source.** Each candidate was traced to its entry in the release-note sources (file and line)
   or in the NumPy 2.0 migration guide (section).
3. **Running.** A minimal call of each candidate was run once in the old and once in the new
   environment: `raises` if it runs in the old version and raises in the new one, `silent` if both
   run but the results differ, `same` otherwise.
4. **Replacement check.** For selected changes, the replacement was run in the new environment and
   its result compared with the result of the old code in the old environment.

A candidate is included if all of the following hold:

1. it is a public API that ordinary data-analysis code uses;
2. it actually breaks in this version range;
3. the release notes or the library give a replacement that is equivalent to the old behavior;
4. it needs no extra packages (such as Excel or a LaTeX engine).

## Results

- 100 candidates: 93 raise an error, 5 change results silently, 2 behave the same (for example,
  NumPy 2.x provides `np.bool` again).
- 75 were included.
- Criterion 1 was later reduced to "public API": the judgment of common use was dropped, which
  re-admits the 11 changes excluded as `rarely used` and gives 86 planned changes.
- The 4 included silent changes raise no error and are not used as test cases. The test cases are
  the 82 planned changes that raise an error.
- All replacements run. Most give identical results, some differ only in display format, and 4 give
  the same values with a different return type or dtype, so the tests compare values.

## Sources

- pandas 2.0.0: <https://github.com/pandas-dev/pandas/blob/v2.0.0/doc/source/whatsnew/v2.0.0.rst>
- NumPy 1.24.0: <https://github.com/numpy/numpy/blob/v1.24.0/doc/source/release/1.24.0-notes.rst>
- NumPy 2.0.0: <https://github.com/numpy/numpy/blob/v2.0.0/doc/source/release/2.0.0-notes.rst>
- NumPy 2.0 migration guide: <https://numpy.org/devdocs/numpy_2_0_migration_guide.html>
