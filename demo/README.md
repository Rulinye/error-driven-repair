# Demo: one test case through the pipeline

`demo.py` walks one test case through the steps of the study (Figure 1 of the thesis) and pauses after
each step:

1. the test case (`test_cases/list.csv`, `test_cases/cases/<id>/old.py`);
2. the old program in the old environment: the test passes, and the old version warns;
3. the same program in the new environment: the original error E0;
4. the five error-message conditions E0–E4, recomputed by the rules of `conditions/error_variants.py`;
5. the documentation conditions, with the BM25 retrieval of `conditions/retrieval.py` recomputed;
6. the prompts, filled in by `runs/prompts.py`, and their ids in the recorded replies;
7. the model's replies recorded in the main runs (`runs/results/<model>/replies.jsonl`);
8. every reply judged again by `runs/score.py` (hidden test and validity checks);
9. the results of the test case for the four models, and the primary contrasts over all 90 test cases.

Each recomputed value is compared with the value stored by the study's scripts. The model replies are
not generated again; they are the replies recorded in the main runs.

```bash
measurements/envs/tools/bin/python demo/demo.py                 # P22 with Qwen2.5-Coder-7B, Enter after each step
measurements/envs/tools/bin/python demo/demo.py --second        # then P01: a fix that passes the test
                                                                # but fails the validity checks
measurements/envs/tools/bin/python demo/demo.py --case P39 --model codellama-7b
measurements/envs/tools/bin/python demo/demo.py --second --no-pause > demo_output.txt   # whole run, no pauses
```

It needs the measurement environments in `measurements/envs` (`old`, `mid`, `new`, `tools`; see
`measurements/README.md`).
