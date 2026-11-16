# Error and documentation conditions

The two factors of the experiment (Sections 3.4 and 3.5 of the thesis), built for every test case in
`test_cases/list.csv`. Run from the repository root, after `bash measurements/run_all.sh` has built the
environments:

```bash
measurements/envs/tools/bin/python conditions/error_variants.py
measurements/envs/tools/bin/python conditions/retrieval.py
measurements/envs/tools/bin/python conditions/py313.py      # E0 under Python 3.13 (Chapter 7)
```

## Error conditions (`error_variants.py` → `results/error_conditions.csv`)

| level | content |
| --- | --- |
| E0 | the exception type and message that the program of the test case raises when its test runs in the new environment, as printed by Python 3.11, including any "Did you mean" suggestion |
| E1 | only the statement that the code fails after the upgrade |
| E2 | E0 without the interpreter's suggestion, URLs, and sentences that contain a hint phrase ("use", "instead", "might want to try") or name an API other than the failing one |
| E3 | E2 plus the correct hint, "Use X instead." or "Remove the argument X.", with X the recorded replacement |
| E4 | E2 plus "Did you mean: 'Y'?", with Y the public attribute or parameter of the same object, module or function closest to the removed name under the interpreter's distance measure (CPython 3.11, `Python/suggestions.c`), without its cutoff, excluding the correct fix |

Written by hand, in `error_variants.py`:

- the correct and the misleading hint of the 9 behavior changes (`BEHAVIOR`), which have no removed
  name, and, for each misleading hint, the edit of the program that follows it (`E4_EDIT`);
- five correct hints whose recorded replacement does not read as a single fix (`E3_OVERRIDE`);
- two kinds of sentence dropped from E2 (`E2_DROP_BY_HAND`): NumPy's alias messages name the builtin
  that replaces the alias, with the same spelling as the failing name, and then refer back to the
  removed suggestion.

Every misleading hint is checked on the test case: the program with Y in place of the removed name (or
edited as a behavior change's misleading hint says) must fail its test in the new environment or fail
the validity checks (`test_cases/validity.py`); otherwise the next closest name is used (column
`e4_check`). The column `failing_line` is the line of the program in which the error is raised.

## Documentation conditions (`retrieval.py`)

- **Corpus** (`results/corpus.csv`): for each library, the release notes in `screening/release_notes/`
  (pandas 2.0.0, 2.1.0, 2.2.0; NumPy 1.24.0, 1.25.0, 1.26.0, 2.0.0, 2.1.0 and the NumPy 2.0 migration
  guide), split into one item per bullet, per table row, or per paragraph. Headings, labels and
  directive lines are not items; the content of a directive, such as a code example, is.
- **Retrieval:** Okapi BM25 (k1 = 1.5, b = 0.75, idf = ln((N − n + 0.5) / (n + 0.5) + 1)) over lowercased
  tokens of letters and digits.

| level | content |
| --- | --- |
| D0 | no documentation |
| D1 | the top three items for the query "failing line + error text of the current condition"; under E1, which has no error and so no failing line, the complete program of the test case |
| D2 | the recorded item for the change (a subsection when the recorded line is its heading), with the deprecation warning of the old version for the same call, if any |
| D3 | D2 together with the two highest-ranked incorrect items for "failing line + E2", in random order (seed 20261026) |

`results/documentation.csv` holds D2, the D3 order, `entry_names_fix` (whether the recorded item itself
names the fix, by reading; it does not for 21 test cases, listed in `ENTRY_NO_FIX`, and for each of them
the old warning does) and `d2_names_fix` (whether an identifier of the correct hint occurs in D2; the 9
behavior changes were decided by reading). `results/retrieval.csv` holds
the top three items and recall@3 for every test case and error level. Correct items are the recorded
item and the release-note items that the screening found to describe the same removed name or
parameter.

## E0 under Python 3.13 (`py313.py` → `results/py313.csv`)

For Chapter 7, the program of every test case runs with its test under Python 3.13 (pandas 2.2.3, NumPy 2.1.3), as
in `error_variants.py`, and the printed error is compared with E0. It differs for 7 of the 90 test cases. Python
3.13 adds a suggestion for a keyword argument in 5 of them: following it gives a correct fix for P20, P22 and P39,
still fails for P32, and gives a wrong result for P35 (`loffset` to `offset`). It drops the suggestion
`_join_monotonic` for P09 and suggests `codes` instead of `_mode` for P14.
