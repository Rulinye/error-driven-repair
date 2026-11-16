# Error-Driven Code Repair for Python Library Upgrades

Code, data and results of the bachelor's thesis *Error-Driven Code Repair for Python Library Upgrades: A
Controlled Study of Error Messages and Documentation in LLM-Based Repair* (Ding Cheng, School of Software,
Chung-Ang University, 2026). The thesis is `thesis/thesis.docx`.

The thesis measures how much the error message, compared with the documentation (the release notes and the
NumPy 2.0 migration guide), helps a large language model repair Python code broken by two library upgrades:
pandas 1.5.3 → 2.2.3 and NumPy 1.23.5 → 2.1.3. Four models (GPT-6 Luna, Gemini 3.8 Flash, Qwen2.5-Coder-7B
and CodeLlama-7B) repair 90 test cases of real changes and 15 of synthetic changes under 20 conditions: five
error conditions (E0–E4) crossed with four documentation conditions (D0–D3).

## Versions

| tag | content |
| --- | --- |
| `plan-frozen` | the hypotheses and the analysis plan (Chapter 4 of the thesis), committed before the first main run |
| `thesis-final` | the version that the submitted thesis describes |

## Folders

In the order of the pipeline (Figure 1 of the thesis):

| folder | content | thesis |
| --- | --- | --- |
| `screening/` | the candidate pool: API comparison, release notes, selection criteria, random draw | 3.2.2 |
| `test_cases/` | the 90 test cases (old program, hidden tests, reference fix), their execution checks, the 30 second test cases and the check of test adequacy | 3.2.3, 3.2.4 |
| `synthetic/` | the 15 synthetic changes: three local packages in two versions, their release notes and test cases | 3.2.5 |
| `conditions/` | the error conditions (E0–E4) and the documentation conditions (D0–D3) of every test case | 3.3–3.5 |
| `probe/` | the knowledge probe: the questions, the answers of the four models and their labels | 3.8 |
| `runs/` | the prompts, the model calls and the judging of every fix (accepted or rejected); the replies of all runs | 3.6, 3.7, 3.9, 6.1 |
| `analysis/` | the analyses of the plan and every number of the results | 4, 6 |
| `measurements/` | builds the Python environments of the study and reruns the pilot study | 5 |
| `examples/multi-change-example/` | the example of Section 1.1: one pandas 1.x script that crashes five times after the upgrade | 1.1 |
| `demo/` | walks one test case through the pipeline, step by step | 3.1 |
| `thesis/` | the thesis (Word) | |

## Recomputing the results

1. Build the environments (macOS or Linux, with [uv](https://docs.astral.sh/uv/)):
   `bash measurements/run_all.sh` (see `measurements/README.md`).
2. Run the analysis scripts listed in `analysis/README.md`. They read the stored replies and write their
   results to `analysis/`. Most need only Python 3 with NumPy; `power.py` also needs SciPy, and
   `logit_check.R` needs R with lme4. The scripts that run fixes (`ruff_baseline.py`, `runs.py`,
   `posthoc.py` and `fix_review_probes/run.py`) use the environments of step 1.
3. The models do not need to be called again: their replies are stored in `runs/results/`, `probe/results/`
   and `synthetic/results/`. To call them again, see `runs/README.md`.

## Terms

The READMEs use the terms of the thesis. Some file and column names keep older words so that the scripts run
unchanged: `entry` (for example in `release_note_entries.csv` and `entry_names_fix`) is an item of the
documentation, and the outcome `correct` in `samples.csv` means that the fix is accepted.

## License

The code is licensed under the MIT License (`LICENSE`). The data and texts written for this study are licensed
under CC BY 4.0 (`LICENSE-DATA.md`). The copies of the pandas and NumPy release notes and other third-party
material keep their own licenses (`THIRD_PARTY_NOTICES.md`).
