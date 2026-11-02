# Knowledge probe

Section 3.8 of the thesis. Before the main runs, each model is asked about each test case, without
code and without an error message. A test case is known to a model if at least three of five sampled
answers give the fix (see below for what counts). H4 is tested on the test cases a model does not know.

```bash
measurements/envs/tools/bin/python probe/questions.py          # -> results/questions.csv
measurements/envs/tools/bin/python probe/score.py --self-check
measurements/envs/tools/bin/python probe/score.py ANSWERS.csv  # -> results/answer_labels.csv, results/known.csv
```

The models answer on the notebooks of `runs/` (`RUN = "probe"`), with the settings of the main runs:

```bash
python probe/requests.py export runs/api_models/requests_probe.jsonl      # the same file serves both notebooks
python probe/requests.py answers MODEL replies_MODEL_probe.jsonl          # -> results/answers.csv, results/MODEL/
measurements/envs/tools/bin/python probe/score.py probe/results/answers.csv
```

On November 2, GPT-6 Luna knew 83 of the 90 test cases and Gemini 3.8 Flash 84 (USD 0.017 and 0.59 for 450
answers each), Qwen2.5-Coder-7B 47 and CodeLlama-7B 36 (16 and 31 minutes on two T4 GPUs); `results/known.csv`
has the labels.

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
- `np.asarray` or `np.array` for `Categorical.to_dense`;
- the module path or an import for N37 and N38 (`np.exceptions.AxisError`,
  `from numpy.exceptions import AxisError`).

`score.py` asks for a hand label for all answers to 12 test cases whose fix is not a name: removing an
argument (P21, P25, P40, P41, P42, P66), assigning the result instead of `inplace=True` (P23, P38), shifting
the index after resampling (P35), and three behavior changes fixed by a conversion (P53, P68, N36); and for
answers that do not match but name an API close to the fix (`NEAR`), such as `np.object_` for `np.object`,
`astype` for `np.cast`, or `infer_dtype` for `Index.inferred_type`. A test case stays `pending` while an
answer that decides its label has no hand label. Hand labels go in `hand_labels.csv` (columns `model`, `id`,
`sample`, `correct` = `yes`/`no`, and the `reason`) and override the automatic match.

An answer is correct if, for the object the question names, at least one recommendation in its text or code
runs and gives the old result wherever the recorded fix gives it (for the two `datetime64[D]` changes, in any
supported resolution, as above), checked by running both in the old and the new environment. The
recommendation can be one of several options; an answer that names the fix only to describe the old version,
as removed, or in passing is not correct. A question about a removed parameter does not give the old value,
so naming the new parameter is enough unless the answer maps the old value wrongly. Results are compared by
value, not by memory sharing. Values that the caller's own code supplies, such as the target dtype for N20,
are not judged. Other APIs that count include `Categorical.to_numpy` for P13, assigning `df.columns` for
P33, `np.array(x, dtype=float)` for N19, `astype` or `np.array(..., dtype=...)` for N20, `np.matrix` for N21,
`np.max(a) - np.min(a)` for N32 and `-float('inf')` for N13.

These do not count:

- another type that passes the test case: the builtin `str` for `np.unicode_` (N09), `np.object_` for the
  builtin `object` (N04), `UserWarning` for `np.VisibleDeprecationWarning` (N38);
- a recommended call that fails: a function that does not exist (`Series.concat`, `types.issubclass`), an
  argument that is rejected (`np.round(x, mode=...)`; a callable `on_bad_lines`, which the default C engine
  rejects), or calling a constant (`np.nan()`);
- a wrong value for a removed parameter: a wrong unit for P34 (`base` counted units of the frequency, so
  `"2H", base=1` is `offset="1h"`); for P36, `"left"` described as excluding the start (it keeps the start
  and excludes the end); for P37, moving the start date instead of `inclusive="left"`;
- a different result: for P16, `pd.api.types.infer_dtype`, which skips missing labels by default, tested with
  `"mixed" in ...` or `.startswith("mixed")`, which also accepts `"mixed-integer"` (`is_mixed()` was true only
  for `"mixed"`); `isocalendar()` without `.week` (P11, P62); `get_indexer([key], ...)` without `[0]` (P43,
  P64); `df.squeeze()` for P31, which returns a scalar for a one-row file; conversions that drop the time for
  P49 and P50; and for P53 and N36 an old result that pandas 1.5.3 and NumPy 1.23.5 do not give (truncation to
  integers, wrapping to `uint8`).

After the first scoring, all 1,800 answers were read in full. The rules above were made explicit during this
reading and applied to the answers of all four models. Outside the 12 test cases labeled by hand in full, the
hand label differs from the automatic match for 14 answers of GPT-6 Luna, 8 of Gemini 3.8 Flash, 46 of
Qwen2.5-Coder-7B and 55 of CodeLlama-7B. The reason for every hand label is in `hand_labels.csv`.

`--self-check` runs the matcher on answers whose label is known: for every test case, the recorded
replacement and the correct hint E3 (`conditions/results/error_conditions.csv`) must match; for the
78 test cases not checked by hand, the misleading name of E4, or for a behavior change the code that
follows the misleading hint, must not match.
