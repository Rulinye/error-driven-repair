# Multi-change example: one pandas 1.x script, five crashes after the upgrade

This folder lets anyone rerun a small example from the thesis
*Error-Driven Code Repair for Python Library Upgrades*: a 50-line report script written in
pandas 1.x style runs under pandas 1.5.3, but under pandas 2.x it crashes five times in a row,
because each crash hides the next broken line. Under Python 3.11 and 3.12, none of the five error
messages names the fix, and one points to a private method.

## What this is, and what it is not

- **A reconstruction.** The author's network-tool backend computed its usage statistics with
  pandas 1.x; that Python code was replaced when the backend was rewritten in Go. `steps/v0.py`
  reconstructs its daily usage report in pandas 1.x style for this thesis (October 2026). It is
  not the original code.
- **Synthetic data.** `gen_data.py` writes seeded synthetic data (usage meters, accounts, nodes,
  node metrics). No real data is included.
- **Not a test of the hypotheses.** No language model is involved. The example only shows how the
  changes surface and what the error messages say.

## Rerun it

Requirements: macOS or Linux with bash, and [uv](https://docs.astral.sh/uv/getting-started/installation/),
which also downloads the Python versions. Windows: use WSL (untested).

```bash
./run_all.sh          # configs old + new (the setup of the thesis)
./run_all.sh all      # also the two "forced upgrade" configs
```

The script creates one virtual environment per config in `.venvs/`, installs the pinned packages
with hash checking (`--require-hashes`, wheels only), writes the data to `data/`, runs every step in
every config, writes everything to `results/`, and compares it with `expected/`. It ends with
`ALL CHECKS PASSED` (exit status 0) or lists each difference (exit status 1).

## Configs

| config | Python | pandas | NumPy | why |
|--------|--------|--------|-------|-----|
| `old` | 3.11.17 | 1.5.3 | 1.23.5 | old environment of the thesis |
| `new` | 3.11.17 | 2.2.3 | 1.23.5 | new environment of the thesis (pandas study) |
| `forced312` | 3.12.9 | 2.1.1 | 1.26.0 | first pandas / NumPy releases with wheels for Python 3.12 |
| `forced313` | 3.13.12 | 2.2.3 | 2.1.0 | first pandas / NumPy releases with wheels for Python 3.13 |

pandas 1.5.3 and NumPy 1.23.5 ship wheels for CPython 3.8–3.11 only, so moving to Python 3.12 or
later forces the upgrade. All transitive dependencies are pinned to the versions used when the
expected results were recorded (2026-10-25), including python-dateutil 3.0.0; see `requirements/`.

## The steps

Each step applies one documented fix to the previous one (`steps/diffs/` shows each change).

| step | change from the previous step |
|------|-------------------------------|
| `v0` | original script |
| `v1` | `Series.iteritems()` → `Series.items()` |
| `v2` | `DataFrame.append` → `pandas.concat` |
| `v2_private_append` | instead of `v2`: follow the interpreter's suggestion and call the private `_append` |
| `v3` | `groupby().mean()` → `groupby().mean(numeric_only=True)` |
| `v4` | `value_counts().reset_index()`: use `rename_axis(...).reset_index(name=...)`, because the column names changed in 2.0 |
| `v5` | `to_csv(line_terminator=)` → `to_csv(lineterminator=)` |
| `v5_private_append` | `v5` with the private `_append` instead of `pandas.concat` |

All five changes are described in the pandas 2.0.0 release notes:
<https://pandas.pydata.org/docs/whatsnew/v2.0.0.html>.

## Expected results

Under `old`, every step runs and writes byte-identical output files, so each fix also works
under pandas 1.5.3. In `results/old/v0/stderr.txt`, pandas 1.5.3 warns about four of the
five changes: three warnings name the replacement ("Use .items instead.", "Use pandas.concat
instead.", "use 'lineterminator' instead."), the `numeric_only` warning says "Either specify
numeric_only or select only columns which should be valid for the function.", and the
`value_counts` change gives no warning at all.

Under `new` (pandas 2.2.3, Python 3.11), the last error line of each step is:

| step | outcome |
|------|---------|
| `v0` | `AttributeError: 'Series' object has no attribute 'iteritems'` |
| `v1` | `AttributeError: 'DataFrame' object has no attribute 'append'. Did you mean: '_append'?` |
| `v2` | `TypeError: agg function failed [how->mean,dtype->object]`; the chained error above it quotes several thousand characters of concatenated values |
| `v3` | `KeyError: 'region'`, raised at line 50, two lines below the `value_counts` call |
| `v4` | `TypeError: NDFrame.to_csv() got an unexpected keyword argument 'line_terminator'` |
| `v5` | runs; output files byte-identical to `v0` under `old` |

`forced312` gives the same five outcomes. Under `forced313` the `v4` error ends with
`Did you mean 'lineterminator'?`, because Python 3.13 also suggests keyword-argument names.
In every 2.x config, `v5_private_append` writes files byte-identical to `v5`, so a test that
compares outputs accepts the private-method fix.

Optional, the rule-based baseline (reports "All checks passed!", meaning it detects none of the five
breaking changes):

```bash
uvx ruff@0.16.10 check --isolated --no-cache --select PD,NPY steps/v0.py
```

## Files

```
run_all.sh            rerun and compare (modes: check, all, record)
gen_data.py           seeded synthetic data, standard library only
steps/v*.py           the script at each step
steps/diffs/          one diff per step
requirements/*.txt    pinned, hashed requirements per config
expected/             recorded results: versions, outcome of each step, SHA-256 of data and outputs
```

`./run_all.sh record` overwrites `expected/` with a new run; it is meant for the maintainer only.

Recorded on macOS 26.6.2 (arm64) with uv 0.12.23 and the system bash 3.2, and rerun on Linux
(x86_64), where all checks pass. Windows has not been tested; if a check fails there, the difference
itself is a result worth reporting.
