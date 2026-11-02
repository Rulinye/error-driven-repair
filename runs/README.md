# Model runs

Prompts, model calls and judging for the main runs (Sections 3.6, 3.9 and 4.2 of the thesis). Run from the
repository root, after `bash measurements/run_all.sh` has built the environments.

```bash
python runs/run.py fake --conditions all --budget 5                 # the pipeline, without a model
python runs/run.py MODEL --conditions primary --estimate            # number of calls and approximate cost
python runs/run.py MODEL --conditions primary --budget 5            # primary conditions first (Section 4.2)
python runs/run.py MODEL --conditions rest --budget 10              # then the remaining levels
python runs/run.py MODEL --random 10 --conditions all --store MODEL-dryrun   # the dry run, kept apart
```

## Open models (`open_models/`)

Qwen2.5-Coder-7B-Instruct (`qwen2.5-coder-7b`) and CodeLlama-7B-Instruct (`codellama-7b`) run on a GPU notebook,
with no API cost:

```bash
python runs/run.py qwen2.5-coder-7b --random 10 --conditions all --store qwen2.5-coder-7b-dryrun --export requests_dryrun.jsonl
# on the notebook (open_models/run_open_models.ipynb, RUN = "dryrun"):
#   python generate_open.py Qwen/Qwen2.5-Coder-7B-Instruct requests_dryrun.jsonl replies_qwen2.5-coder-7b_dryrun.jsonl --batch 8
python runs/run.py qwen2.5-coder-7b --random 10 --conditions all --store qwen2.5-coder-7b-dryrun --import replies_qwen2.5-coder-7b_dryrun.jsonl
```

`--export` writes the prompts and samples that are still missing; `--import` adds the replies, judges them like
any other, and keeps the notebook's `.meta.json` with the results. `generate_open.py` uses the model's chat format with the prompt as the only message, and the
model's own generation config except for the temperature (0.2) and the limit of 2,048 new tokens. The model is
spread over all GPUs, in bfloat16 on GPUs with native bfloat16 (compute capability 8.0 or higher) and in float16
on older ones such as the T4, which only emulates bfloat16 and is then several times slower. The GPUs, library
versions, sampling parameters in effect, batch size and GPU time are written to `<replies>.meta.json`. A session
that was cut off resumes where it stopped. A 7B model needs about 15 GB in 16-bit precision, so one 16 GB T4 is
not enough for Qwen2.5-Coder-7B; on 2 × T4, Qwen2.5-Coder-7B takes 8 prompts per batch and CodeLlama-7B, whose
attention keeps a larger cache per token, 2.

The dry run uses 10 test cases drawn with the seed 20261031 (P06, P11, P31, P33, P35, P36, P44, P63, N07, N12),
all 20 conditions and 5 samples: 160 distinct prompts, 800 samples per model. It ran on 2 × T4 on November 1,
still in emulated bfloat16 and with 2 prompts per batch: 55.7 GPU minutes for Qwen2.5-Coder-7B (median reply 49
tokens, longest 133) and 155.8 for CodeLlama-7B (median 118, longest 631); no reply reached the token limit.
Results in `results/<model>-dryrun/`. The speed test (`requests_speedtest.jsonl`) repeated 20 of these prompts,
spread over the prompt lengths (100 samples per model), on November 2 in float16 with the batch sizes above:
58 GPU seconds for Qwen2.5-Coder-7B (0.58 s per sample, 85 of 100 correct as in the dry run, 96 with identical
code) and 207 for CodeLlama-7B (2.1 s per sample, 51 correct against 56 in the dry run, lower on 4 of the 20
prompts and higher on none). Results in `results/<model>-speedtest/`; the model commits that Kaggle recorded for
both runs are in `results/open_model_revisions.json`, and `generate_open.py` loads these commits in every run.

## Commercial models (`api_models/`)

GPT-6 Luna (`gpt-6-luna`, OpenAI) and Gemini 3.8 Flash (`gemini-3.8-flash`, Google) are called through their APIs
from a notebook with Internet access (`api_models/run_api_models.ipynb`; no GPU), with the same `--export` and
`--import` as the open models. `generate_api.py` sends one request per sample with the prompt as the only message
and at most 2,048 output tokens: GPT-6 Luna through Chat Completions with reasoning effort `none` and temperature
0.2; Gemini 3.8 Flash through `generateContent` with thinking level `low`, the lowest it accepts (its thinking
tokens are billed as output and count toward the output limit). The keys are read from `OPENAI_API_KEY` and
`GEMINI_API_KEY` (on Kaggle, from the notebook's secrets) and are never printed or written.

The cost of every reply is computed from the token counts that the API reports and the standard prices (USD per
million tokens, input / output, through December 31, 2026): GPT-6 Luna 0.10 / 0.50, Gemini 3.8 Flash 0.75 / 3.75.
Before each request, the cost of the replies file so far plus the most that the request can cost must stay within
`--budget`. Rate limits and server errors are retried; any other error stops the script with the API's message.
The settings, prices, calls, cost and call dates are written to `<replies>.meta.json`.

The smoke test on November 2 sent 3 prompts of the dry run (two of P06, one of P11), 2 samples each, to both
models, and to Gemini 3.8 Flash also at its default temperature, which Google recommends for Gemini 3 models.
All 18 replies were correct, with the same code at both temperatures, and none came close to the token limit;
Gemini 3.8 Flash used up to 255 thinking tokens per reply at 0.2 and up to 372 at the default. Results in
`results/<model>-smoke/` and `results/gemini-3.8-flash-default-smoke/`. Both commercial models are run at 0.2,
like the open models.

The dry run (the 10 test cases, 20 conditions and 5 samples of the open models' dry run, 800 samples per model)
ran on November 2 with 4 requests at a time. GPT-6 Luna took 4.8 minutes and cost USD 0.038 (median reply 50
tokens, longest 81). Gemini 3.8 Flash took 9.6 minutes and cost USD 0.59 (median 58 output tokens, thinking
included; 596 of the 800 replies without thinking). Two Gemini 3.8 Flash replies, for P33 and P35, used the whole
limit of 2,048 output tokens, almost all of it for thinking, and contain no complete code block. Results in
`results/<model>-dryrun/`.

## Prompts (`prompts.py`)

One template for every condition, and a paraphrased template for the sensitivity check on the six conditions of
the primary contrasts (`--template paraphrase`). The main template:

````
This code was written for {library} {old version} and is now run with {library} {new version}.

```python
{old program}
```

Error:
```
{error text of the condition}
```

Documentation:
{documentation of the condition}

Fix the code so that it works with {library} {new version}. Return only the complete fixed code in one Python code block.
````

- E1 has no error: the statement that the code fails after the upgrade takes the place of the error block.
- D0 has no documentation block. D1, D2 and D3 have the same heading.
- The versions are pandas 1.5.3 and 2.2.3, and NumPy 1.23.5 and 2.1.3.
- Conditions of one case whose prompts are identical share one prompt: 1,512 distinct prompts for the 90 test
  cases and 20 conditions instead of 1,800.

## Calls and budget (`run.py`, `backends.py`)

- Replies are stored per model in `results/<model>/replies.jsonl` (or `results/<name>/` with `--store`), one line
  per prompt and sample, with the tokens and the cost. A prompt is sampled only once, also across calls of the
  script, and an interrupted run continues where it stopped.
- Before every call, the cost so far plus the most that one call can cost must stay within `--budget` and within
  `TOTAL_BUDGET` (USD 25) over all replies of billable models; otherwise the script stops.
- Sampling: 5 samples per prompt at temperature 0.2, at most 2,048 output tokens.
- Backends: `fake` answers with the files of the test case (sample 0 the reference fix, 1 the wrong fix or the old
  program, 2 the old program, 3 no code, 4 the reference fix after a bash block), so two of every five samples
  are correct. The model backends are added with the models.

## Judging (`score.py`)

| outcome | meaning |
| --- | --- |
| `correct` | the test passes in the new environment within 60 seconds and the fix passes the validity checks |
| `fails the validity checks` | the test passes, but the fix uses a private name, monkey-patches, or adds a broad except clause or a warning filter (`test_cases/validity.py`) |
| `fails the test` | the test fails, raises an error, or times out |
| `no code block` | the reply has no closed code block marked python, py or python3, or unmarked |

The first such code block of the reply is the fix. As in Markdown, a fence may be indented by up to three spaces
(CodeLlama's replies begin with a space before the first fence); the indentation is removed from the lines of the
block only where all of them have it, so the code itself is never changed. Library warnings raised while the test runs are recorded in
`warnings`; such fixes are still correct (Section 3.9). Four reference fixes raise one (P34, P35, P39 and N21).

Output, in the folder of the model: `samples.csv` (one row per case, condition and sample; a shared sample appears
under each of its conditions, with their number in `shared`), `judged.jsonl` (the cache of judged code per case)
and `summary.txt` (pass@1 per condition, outcomes, tokens and cost).

With the fake backend on all 90 test cases and 20 conditions, pass@1 is 0.400 in every condition, as expected.
