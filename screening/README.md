# Screening

This folder builds the candidate pool for the test cases (Section 3.2.2 of the thesis): a table with
one row per change that may break old code. Each row is then checked against the selection
criteria (see `measurements/data/README.md`).

The pool has two sources:

1. **API comparison** (this step): a program lists the public API of the old and the new version of
   each library and compares the two lists.
2. **Release notes**: the official notes of every release in the version range, read entry by
   entry, for changes the comparison cannot find (next step).

## API comparison

| file | purpose |
| --- | --- |
| `api_dump.py` | lists the public API of one installed version |
| `api_diff.py` | compares two listings and writes one row per removed attribute or removed parameter |
| `run_api_diff.sh` | runs both for pandas and for NumPy |

Run from the repository root, after `bash measurements/run_all.sh` has built the environments:

```bash
bash screening/run_api_diff.sh
```

Pairs of versions:

- pandas 1.5.3 → 2.2.3, with NumPy 1.23.5 in both, so that NumPy changes do not mix in
- NumPy 1.23.5 → 2.1.3, with pandas 2.2.3 in both

### Scope and rules

- **Objects inspected.** The namespaces each library documents for general use:
  - pandas: the public API as the [pandas API reference](https://pandas.pydata.org/pandas-docs/version/1.5/reference/index.html)
    defines it: the top-level namespace and the public subpackages `pandas.api.types`,
    `pandas.api.extensions`, `pandas.api.indexers`, `pandas.api.interchange`, `pandas.arrays`,
    `pandas.errors`, `pandas.plotting`, `pandas.testing` and `pandas.tseries.offsets`. From
    `pandas.io` and `pandas.tseries`, only the names the reference documents:
    `pandas.io.json.build_table_schema`, `pandas.io.stata.StataReader` and `StataWriter`, and
    `pandas.tseries.frequencies.to_offset`. `pandas.core`, `pandas.compat` and `pandas.util` are
    private according to the reference.
  - NumPy: the main namespaces listed in [NumPy's module structure](https://numpy.org/doc/2.1/reference/module_structure.html)
    that exist in NumPy 1.23.5: `numpy`, `numpy.fft`, `numpy.linalg`, `numpy.polynomial` (with
    its submodules), `numpy.random`, `numpy.testing` and `numpy.typing`. The special-purpose
    namespaces (such as `numpy.lib`) and the legacy namespaces (such as `numpy.ma` and
    `numpy.matlib`) are not included.
  - In both: every class of the library that one of these namespaces exposes, the singletons
    `pd.NaT` and `pd.NA`, the `.dt`/`.str`/`.cat` accessors, and the objects returned by groupby,
    resample, rolling, expanding and ewm.
- **Public.** A member is public if its name does not start with an underscore.
- **Hidden names.** Names that a module serves through its module-level `__getattr__` are included
  (for example `np.float` in NumPy 1.23.5 and `pd.np` in pandas 1.5.3), except placeholders that
  exist only to raise an error.
- **Use, not only presence.** Members of classes are also accessed on a sample object, because some
  removed members remain on the class and fail only on use (for example `ndarray.ptp` in NumPy 2.x).
  This is done for DataFrame, Series, the Index classes, Categorical, Timestamp, Timedelta, Period,
  the accessor and groupby-like objects, `pd.NaT` and `pd.NA`, and in NumPy for `ndarray`, the scalar
  types, `finfo`, `iinfo` and `dtype`. A member that only an instance provides (through the instance's
  `__getattr__`) counts as present if the sample object has it.
- **Platform leftovers excluded.** `numpy/__init__.py` of NumPy 1.23.5 leaves temporary variables
  behind on some platforms only (`w` and `error_message` on macOS, `kernel_version` on Linux). They
  are not part of the API and are excluded, so that the result is the same on every computer.
- **Inherited members once.** A change is listed once under the class that defines it; `seen_on`
  lists the inspected objects that have it. DataFrame and Series do not inherit from each other, so
  a member each of them defines is listed twice. A class removed as a whole is one row; its members
  are not listed separately.

### Output (`results/`)

- `pandas_old.json`, `pandas_new.json`, `numpy_old.json`, `numpy_new.json`: the listings
- `pandas_api_diff.csv`, `numpy_api_diff.csv`: the differences, with the columns

| column | meaning |
| --- | --- |
| `change` | `removed attribute` or `removed parameter` |
| `defined_in` | the class or module that defines the member |
| `name` | the member |
| `parameter` | the removed parameter (removed parameters only) |
| `kind` | class, function, method, attribute, value or module |
| `seen_on` | inspected objects that have the member |
| `hidden_in_old` | `yes` if the old version served the name through `__getattr__` |
| `new_accepts_any_keyword` | `yes` if the new version accepts arbitrary keyword arguments, so passing the old parameter may not raise; checked by running |
| `candidate` | id in `measurements/data/changes.csv` if the change is one of the 100 candidates |

### What the comparison cannot find

- behavior changes, where names and parameters stay the same (for example `groupby().mean()` with
  text columns)
- parameters whose old name the old version accepted through a wrapper, so that the old signature
  already shows only the new name (for example `to_csv(line_terminator=...)`)
- arguments that are not in the signature the comparison reads, such as those of `DataFrame.plot`
- special methods, such as calling a `DateOffset` (`__call__`)
- members of `Styler`, whose module cannot be imported without jinja2
- options (`pd.set_option`)

These come from the release notes.

## Release notes

`release_notes/` holds the official release notes of every release in the version range, taken
from the release tags of the two repositories, and the NumPy 2.0 migration guide:

| file | source |
| --- | --- |
| `pandas_2.0.0.rst`, `pandas_2.1.0.rst`, `pandas_2.2.0.rst` | `doc/source/whatsnew/v2.x.0.rst` at tags `v2.0.0`, `v2.1.0`, `v2.2.0` of pandas-dev/pandas |
| `numpy_1.24.0.rst` … `numpy_2.1.0.rst` | `doc/source/release/<version>-notes.rst` at the matching tag of numpy/numpy |
| `numpy_2.0_migration_guide.rst` | `doc/source/numpy_2_0_migration_guide.rst` at tag `v2.0.0` |

`release_note_entries.py` splits the sections that the maintainers mark as affecting existing code
into entries and writes `results/release_note_entries.csv`:

- pandas: Backwards incompatible API changes, Removal of prior version deprecations/changes,
  Notable bug fixes
- NumPy: NumPy 2.0 Python API removals, Expired deprecations, Compatibility notes, Changes; from the
  migration guide, Changes to NumPy data type promotion and Other changes

Deprecations are not read, because deprecated code still runs and only warns. New features,
improvements, performance, bug fixes, C API and build changes are not read either.

```bash
measurements/envs/tools/bin/python screening/release_note_entries.py
```

| column | meaning |
| --- | --- |
| `entry` | library, release and line of the entry |
| `section` | section of the release notes |
| `line` | line in the file in `release_notes/` |
| `api_rows` | rows of the API comparison whose names the entry mentions |
| `candidates` | ids in `measurements/data/changes.csv` whose recorded source line is in this entry |
| `text` | the entry, with markup removed |

### Decision on each entry

`release_note_decisions.py` records, for every entry, whether it adds a row to the candidate pool,
with a one-line reason, and writes `results/release_note_decisions.csv`:

| category | meaning | pool row |
| --- | --- | --- |
| `api` | the change is already a row of the API comparison | no |
| `api+removal` | part of the entry is a row of the API comparison, part is a removal it misses | yes, for the missed part |
| `removal` | a removal the API comparison misses | yes |
| `raises` | a behavior change that makes code that ran in the old version raise | yes |
| `silent` | a behavior change without an error | no (silent changes are not test cases) |
| `out_of_scope` | concerns an object outside the scope of the API comparison: not public, or in a NumPy namespace that is not a main namespace | no |
| `other` | build, dependencies, C API, platform, new capability, only the error type changes, or the old code still runs with a warning | no |

An entry that describes one change for several related objects (for example `DataFrame.drop` and
`Series.drop`) adds one pool row. Matching names automatically (column `api_rows` of
`release_note_entries.csv`) is only a first filter, so every entry was decided by reading it.

```bash
measurements/envs/tools/bin/python screening/release_note_decisions.py
```

## Candidate pool

`build_pool.py` combines both sources into `results/pool.csv`, one row per change:

| id | source |
| --- | --- |
| `A-P-nnn`, `A-N-nnn` | a row of the API comparison (pandas, NumPy) |
| `R-P-nnn`, `R-N-nnn` | a release-note entry of category `removal`, `raises` or `api+removal` |
| `C-xxx` | an earlier candidate that neither source lists |

Rows that are one of the 100 earlier candidates carry the earlier decision and are not examined
again. For every other row, the four criteria are checked in the order that saves work: criterion 1
(public API) and criterion 4 (no extra packages) first, then criterion 3 (a documented replacement),
and only then criterion 2 and the replacement, by running code in both versions.

Criteria 1 and 4 are applied by `criteria.py`:

- **Criterion 1.** Within the scope of the API comparison, a row is not public if NumPy 1.23.5 itself
  marks it so (`numpy/tests/test_public_api.py`: the objects "not publicly documented to be part of
  the main NumPy namespace", and the private modules `numpy.compat` and `numpy.linalg.lapack_lite`),
  if it is a module of the Python standard library (`numpy.os`, `numpy.sys`, `numpy.math`,
  `numpy.warnings`), or if it is a placeholder (`numpy.oldnumeric` and `numpy.numarray` are the
  string `'removed'`).
- **Criterion 4.** A row fails if the code needs openpyxl (Excel), PyTables (HDFStore), matplotlib
  (plotting), jinja2 (Styler, and `to_latex` in pandas 2.x), tabulate (`to_markdown`) or nose (NumPy's
  old nose support).

| column | meaning |
| --- | --- |
| `change` | what changed |
| `candidate` | id in `measurements/data/changes.csv`, for earlier candidates |
| `entry` | release-note entry, for rows from the release notes |
| `c1_public`, `c4_no_extra_package` | `yes` or `no` |
| `c3_replacement`, `c3_source` | the documented replacement and where it is documented |
| `c2_old_code`, `c2_raises_in_new` | old code, and whether it runs in the old version and raises in the new one |
| `c3_new_code`, `c3_same_result` | the replacement, and whether it gives the old result |
| `decision`, `reason` | `included` or `excluded`, and why |

```bash
measurements/envs/tools/bin/python screening/build_pool.py
```
