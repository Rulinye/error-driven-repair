# Error and documentation conditions

The two factors of the experiment (Sections 3.4 and 3.5 of the thesis), built for every test case in
`test_cases/list.csv`. Run from the repository root, after `bash measurements/run_all.sh` has built the
environments:

```bash
measurements/envs/tools/bin/python conditions/error_variants.py
measurements/envs/tools/bin/python conditions/retrieval.py
```

## Error conditions (`error_variants.py` → `results/error_conditions.csv`)

| level | content |
| --- | --- |
| E0 | the exception type and message as printed by Python 3.11 in the new environment, including any "Did you mean" suggestion |
| E1 | only the statement that the code fails after the upgrade |
| E2 | E0 without the interpreter's suggestion, URLs, and sentences that contain a suggestion phrase ("use", "instead", "might want to try") or name an API other than the failing one |
| E3 | E2 plus the correct hint, "Use X instead." or "Remove the argument X.", with X the recorded replacement |
| E4 | E2 plus "Did you mean: 'Y'?", with Y the public attribute or parameter of the same object, module or function closest to the removed name under the interpreter's distance measure (CPython 3.11, `Python/suggestions.c`), without its cutoff, excluding the correct fix |

Written by hand, in `error_variants.py`:

- the correct and the misleading hint of the 9 behavior changes (`BEHAVIOR`), which have no removed
  name; each misleading hint comes with the code of a fix that follows it;
- five correct hints whose recorded replacement does not read as a single fix (`E3_OVERRIDE`);
- two kinds of sentence dropped from E2 (`E2_DROP_BY_HAND`): NumPy's alias messages name the builtin
  that replaces the alias, with the same spelling as the failing name, and then refer back to the
  removed suggestion.

Every misleading hint is checked: the old code with Y in place of the removed name (or the fix written
for a behavior change) must fail in the new version or give a different value, type or dtype than the
old code in the old version; otherwise the next closest name is used (column `e4_check`).

The check and the column `failing_line` use the minimal call of each change. Both are repeated once the
programs and tests of the test cases are written, because the tests decide what counts as a correct fix.

## Documentation conditions (`retrieval.py`)

- **Corpus** (`results/corpus.csv`): for each library, the release notes in `screening/release_notes/`
  (pandas 2.0.0, 2.1.0, 2.2.0; NumPy 1.24.0, 1.25.0, 1.26.0, 2.0.0, 2.1.0 and the NumPy 2.0 migration
  guide), split into one chunk per bullet entry, per table row, or per paragraph. Headings, labels and
  directive lines are not chunks; the content of a directive, such as a code example, is.
- **Retrieval:** Okapi BM25 (k1 = 1.5, b = 0.75, idf = ln((N − n + 0.5) / (n + 0.5) + 1)) over lowercased
  tokens of letters and digits.

| level | content |
| --- | --- |
| D0 | no documentation |
| D1 | the top three chunks for the query "failing line + error text of the current condition"; under E1, the failing line alone |
| D2 | the recorded entry for the change (a subsection when the recorded line is its heading), with the deprecation warning of the old version for the same call, if any |
| D3 | D2 together with the two highest-ranked incorrect chunks for "failing line + E2", in random order (seed 20261026) |

`results/documentation.csv` holds D2, the D3 order and `d2_names_fix` (whether an identifier of the
correct hint occurs in D2; the 9 behavior changes are decided by reading). `results/retrieval.csv` holds
the top three chunks and recall@3 for every test case and error level. Correct chunks are the recorded
entry and the release-note entries that the screening found to describe the same removed name or
parameter.
