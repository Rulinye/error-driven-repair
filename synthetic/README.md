# Synthetic API changes

Section 3.2.5 of the thesis: 15 API changes that no model can have seen, from three small local packages,
each released in two versions with five changes. They form the part of H4 that is free of memorization.

```bash
measurements/envs/tools/bin/python synthetic/build.py      # execution checks, conditions, probe questions
python synthetic/probe.py export requests_probe_synthetic.jsonl
python runs/run.py MODEL --set synthetic --conditions all --export requests_synthetic.jsonl
```

## Packages (`packages/<library>/<version>/`) and release notes (`release_notes/`)

| package | old | new | what it does |
| --- | --- | --- | --- |
| fernledger | 1.6.0 | 2.0.0 | ledgers of dated amounts on named accounts |
| gridwell | 0.9.4 | 1.0.0 | small numeric grids stored as lists of rows |
| quillery | 3.2.1 | 4.0.0 | cleaning, splitting and laying out plain text |

The packages are pure Python and need no installation: a program runs with the old or the new version on
`PYTHONPATH`, under the Python 3.11 environment of `measurements/`. The names of the packages were checked to
be free on PyPI on November 3, 2026.

Each new version renames or removes three functions or methods and removes or replaces two parameters. No
replacement is a synonym, abbreviation or spelling variant of the old name. Like NumPy 2.0, gridwell 1.0 answers
the two functions it removed with its own message, which names the replacement; the other errors are those of
Python itself. Each package has one release note of eight items: one for each of its five changes and three
for other changes. The release note is the retrieval corpus of its package (D1 and D3). The other changes do
not affect the test cases: the functions they change are either not used or called only with inputs on which
both versions agree.

## Test cases (`cases/S01` to `cases/S15`, `list.csv`)

The same files as `test_cases/cases/`: `old.py`, `test.py`, `fixed.py`, `wrong.py` where a plausible wrong
fix exists (10 of 15), and `meta.json`. Each case uses one changed function.

| id | change | replacement |
| --- | --- | --- |
| S01 | `fernledger.parse_entries` | `fernledger.read_journal` |
| S02 | `Ledger.tally` | `Ledger.bucketize` |
| S03 | `start` of `Ledger.running_total` | `opening` |
| S04 | `thousands=True` of `fmt_amount` | `style="grouped"` |
| S05 | `fernledger.merge` | `fernledger.chain` |
| S06 | `gridwell.row_means` | `gridwell.collapse(g, "mean", axis=1)` |
| S07 | `Grid.neighbors` | `Grid.ring` |
| S08 | `wrap=True` of `smooth` | `boundary="periodic"` |
| S09 | `gridwell.peak_index` | `gridwell.locate(g, "max")` |
| S10 | `reps` of `tile` | `layout` |
| S11 | `quillery.slugify` | `quillery.to_handle` |
| S12 | `Tokenizer.words` | `Tokenizer.scan` |
| S13 | `width` of `wrap` | `measure` |
| S14 | `strip_accents=True` of `normalize` | `fold="ascii"` |
| S15 | `quillery.word_count` | `quillery.digest(text).words` |

## Results (`results/`)

`build.py` writes, in the formats of `test_cases/results/` and `conditions/results/`: `checks.csv` (all 15 pass
the execution checks), `error_conditions.csv`, `corpus.csv` (24 items), `documentation.csv`, `retrieval.csv` and
`questions.csv`. `runs/prompts.py` reads them together with the conditions of the 90 test cases.

`probe.py` keeps the answers of the knowledge probe (`answers.csv`, `probe/<model>/`) and their labels
(`answer_labels.csv`, `known.csv`), with the rule of `probe/README.md`.
