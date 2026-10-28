# Knowledge probe

Section 3.8 of the thesis. Before the main runs, each model is asked about each test case, without
code and without an error message. A test case is known to a model if at least three of five sampled
answers give the recorded fix. The label is a per-model moderator (H4).

```bash
measurements/envs/tools/bin/python probe/questions.py          # -> results/questions.csv
measurements/envs/tools/bin/python probe/score.py --self-check
measurements/envs/tools/bin/python probe/score.py ANSWERS.csv  # -> results/answer_labels.csv, results/known.csv
```

## Questions (`questions.py` → `results/questions.csv`)

| type | question |
| --- | --- |
| removed API (55) | In <library> <new version>, <old API> was removed. What should be used instead? |
| removed parameter (26) | In <library> <new version>, the parameter <parameter> of <function> was removed. How should a call that uses it be changed? |
| behavior change (9) | In <library> <new version>, the behavior of <call> changed. What argument or conversion keeps the old result? |

The new versions are pandas 2.2.3 and NumPy 2.1.3. The question is the whole prompt.

## Matching the answers

`SPEC` in `questions.py` gives, for each test case, the ways an answer can give the recorded fix: each
alternative is a list of identifiers or regular expressions that must all occur in the answer. The
identifiers are those of the fix, not of the old API, so an answer that only repeats the question does
not match. Some fixes accept more than one spelling of the same fix:

- the builtin or the NumPy type where the record names both (`float` or `np.float64` for `np.float`);
- any supported resolution for the two `datetime64[D]` changes (`s`, `ms`, `us`, `ns`), since
  pandas 1.5.3 returned `datetime64[ns]`;
- `np.asarray` or `np.array` for `Categorical.to_dense`.

Answers are checked by hand:

- for all answers to 12 test cases whose fix is not a name: removing an argument (P21, P25, P40,
  P41, P42, P66), assigning the result instead of `inplace=True` (P23, P38), shifting the index after
  resampling (P35), and three behavior changes fixed by a conversion (P53, P68, N36);
- for answers that do not match but name an API close to the fix (`NEAR`), such as `np.object_` for
  `np.object` or `astype` for `np.cast`.

Hand labels go in `hand_labels.csv` (columns `model`, `id`, `sample`, `correct` = `yes`/`no`) and
override the automatic match. A test case stays `pending` while an answer that decides its label has
not been checked.

`--self-check` runs the matcher on answers whose label is known: for every test case, the recorded
replacement and the correct hint E3 (`conditions/results/error_conditions.csv`) must match; for the
78 test cases not checked by hand, the misleading name of E4, or for a behavior change the code that
follows the misleading hint, must not match.
