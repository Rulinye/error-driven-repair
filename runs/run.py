"""Run a model on the test cases and judge its replies (Sections 3.6, 3.9 and 4.2).

usage: python runs/run.py MODEL [--cases ID ... | --random N | --set synthetic|second]
                          [--conditions primary|rest|all|paraphrase|E2D0,...]
                          [--template main|paraphrase] [--samples 5] [--budget USD] [--estimate]
                          [--store NAME] [--export FILE | --import FILE]

Replies are stored per model in runs/results/<model>/replies.jsonl (or runs/results/<NAME>/ with --store,
for example to keep the dry run apart from the main runs), one line per prompt and sample, keyed by the
prompt id. A prompt that several conditions share, in one call of this script or across calls (the
primary conditions first and the rest later), is sampled only once (Section 4.2). The file is appended to
after every reply, so an interrupted run continues where it stopped and no call is paid twice.

Budget: before every call, the cost so far plus the most that one call can cost must stay within --budget
for this call of the script and within TOTAL_BUDGET over all replies of billable models in runs/results/;
otherwise the script stops.
--estimate prints the number of calls and their approximate cost without calling the model.

Open and commercial models run on a notebook instead: --export writes the prompts and samples still missing
to a file for runs/open_models/generate_open.py or runs/api_models/generate_api.py, and --import adds the
replies it wrote, with their cost, and keeps its .meta.json (settings, GPUs or prices, GPU time or call
dates) in the folder of the results. --random N takes N test
cases drawn with the seed DRY_RUN_SEED, for the dry run. With --template paraphrase and no --cases, the test
cases are the PARAPHRASE_CASES drawn with the seed PARAPHRASE_SEED (20% of the 90), for the sensitivity check
of Section 3.6; store their replies apart (--store MODEL-paraphrase), because samples.csv and summary.txt
are written for the prompts of each call. --set synthetic runs the 15 synthetic test cases (Section 3.2.5),
stored in runs/results/<model>-synthetic/ unless --store is given; --set second runs the 30 second test cases of
the replication subset (Section 3.2.3), stored in runs/results/<model>-second/.

Every reply is judged by runs/score.py; results are cached per case and code, because replies at
temperature 0.2 often repeat. Output, in the same folder: samples.csv, one row per case, condition and
sample (a sample that several conditions share appears under each of them, with the number of conditions
in `shared`), and summary.txt.
"""
import argparse
import csv
import hashlib
import json
import os
import random
import shutil
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

from backends import API, BACKENDS, BILLABLE, MAX_OUTPUT_TOKENS, OPEN, PRICES, approx_tokens, cost
from prompts import ALL, PARAPHRASE, PRIMARY, REST, Conditions, plan
from score import case_dir, extract, judge

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(HERE, "results")
TOTAL_BUDGET = 25.0
SETS = {"primary": PRIMARY, "rest": REST, "all": ALL, "paraphrase": PARAPHRASE}
DRY_RUN_SEED = 20261031
PARAPHRASE_SEED = 20261103
PARAPHRASE_CASES = 18


def paraphrase_cases(conds):
    """The test cases of the sensitivity check with the paraphrased template (Section 3.6)."""
    return sorted(random.Random(PARAPHRASE_SEED).sample(conds.cases, PARAPHRASE_CASES), key=conds.cases.index)


def read_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def spent_total():
    """Cost of all replies of billable models so far, over every folder in runs/results/."""
    if not os.path.isdir(OUT):
        return 0.0
    return sum(r["cost"] for d in os.listdir(OUT) for r in read_jsonl(os.path.join(OUT, d, "replies.jsonl"))
               if r["model"] in BILLABLE)


def estimate(model, prompts, todo):
    price_in, price_out = PRICES[model]
    tokens_in = sum(approx_tokens(prompts[pid]["text"]) for pid, _ in todo)
    fixed = {}
    for pid, _ in todo:
        cid = prompts[pid]["case"]
        if cid not in fixed:
            with open(os.path.join(case_dir(cid), "fixed.py"), encoding="utf-8") as f:
                fixed[cid] = approx_tokens(f.read()) + 10
    tokens_out = sum(fixed[prompts[pid]["case"]] for pid, _ in todo)
    usd = (tokens_in * price_in + tokens_out * price_out) / 1e6
    print(f"{len(todo)} calls, about {tokens_in:,} input and {tokens_out:,} output tokens "
          f"(if the reply is only the code): about USD {usd:.2f} at USD {price_in}/{price_out} per million")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model", choices=sorted(set(BACKENDS) | set(OPEN) | set(API)))
    ap.add_argument("--cases", nargs="*")
    ap.add_argument("--random", type=int, help="N test cases drawn with DRY_RUN_SEED")
    ap.add_argument("--set", default="real", choices=["real", "synthetic", "second"])
    ap.add_argument("--conditions", default="primary")
    ap.add_argument("--template", default="main", choices=["main", "paraphrase"])
    ap.add_argument("--samples", type=int, default=5)
    ap.add_argument("--budget", type=float, default=1.0)
    ap.add_argument("--estimate", action="store_true")
    ap.add_argument("--envs", default=os.path.join(ROOT, "measurements", "envs"))
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--store", help="folder name in runs/results/ (default: the model)")
    ap.add_argument("--export", help="write the missing prompts and samples for a GPU notebook")
    ap.add_argument("--import", dest="import_file", help="add replies written by generate_open.py")
    a = ap.parse_args()

    conds = Conditions()
    cases = a.cases or conds.cases
    if a.random:
        cases = sorted(random.Random(DRY_RUN_SEED).sample(conds.cases, a.random), key=conds.cases.index)
        print("cases:", " ".join(cases))
    elif a.set in ("synthetic", "second") and not a.cases:
        cases = getattr(conds, a.set)
        a.store = a.store or f"{a.model}-{a.set}"
    elif a.template == "paraphrase" and not a.cases:
        cases = paraphrase_cases(conds)
        print("cases:", " ".join(cases))
    conditions = SETS.get(a.conditions) or a.conditions.split(",")
    prompts = plan(conds, cases, conditions, a.template)
    folder = os.path.join(OUT, a.store or a.model)
    os.makedirs(folder, exist_ok=True)
    replies_path = os.path.join(folder, "replies.jsonl")
    done = {(r["prompt_id"], r["sample"]) for r in read_jsonl(replies_path)}
    todo = [(pid, s) for pid in prompts for s in range(a.samples) if (pid, s) not in done]
    print(f"{len(cases)} cases x {len(conditions)} conditions: {len(prompts)} distinct prompts, "
          f"{len(prompts) * a.samples} samples, {len(todo)} still to call")
    if a.estimate:
        estimate(a.model, prompts, todo)
        return
    if a.export:
        samples = defaultdict(list)
        for pid, s in todo:
            samples[pid].append(s)
        with open(a.export, "w", encoding="utf-8") as f:
            for pid, ss in samples.items():
                f.write(json.dumps({"prompt_id": pid, "case": prompts[pid]["case"], "text": prompts[pid]["text"],
                                    "samples": ss}) + "\n")
        print(f"wrote {len(samples)} prompts ({len(todo)} samples) to {a.export}")
        return
    if a.import_file:
        added = 0
        with open(replies_path, "a", encoding="utf-8") as out:
            for r in read_jsonl(a.import_file):
                if (r["prompt_id"], r["sample"]) in done or r["prompt_id"] not in prompts:
                    continue
                done.add((r["prompt_id"], r["sample"]))
                out.write(json.dumps({"model": a.model, "prompt_id": r["prompt_id"], "sample": r["sample"],
                                      "case": r["case"], "text": r["text"], "input_tokens": r["input_tokens"],
                                      "output_tokens": r["output_tokens"], "stop": r["stop"],
                                      "cost": r.get("cost", 0.0), "gpu_seconds": r.get("gpu_seconds", 0.0),
                                      "reasoning_tokens": r.get("reasoning_tokens", 0)}) + "\n")
                added += 1
        print(f"imported {added} replies from {a.import_file}")
        meta = a.import_file + ".meta.json"
        if os.path.exists(meta):
            shutil.copy(meta, os.path.join(folder, os.path.basename(meta)))
    elif a.model in OPEN or a.model in API:
        ap.error("this model runs on a notebook: use --export, then --import (see runs/README.md)")
    else:
        call_model(a, prompts, todo, replies_path)
    judge_and_report(a, conds, cases, conditions, prompts, folder, replies_path)


def call_model(a, prompts, todo, replies_path):
    call = BACKENDS[a.model]
    price_in, price_out = PRICES[a.model]
    run_spent = 0.0
    total = spent_total() if a.model in BILLABLE else 0.0
    with open(replies_path, "a", encoding="utf-8") as out:
        for pid, s in todo:
            p = prompts[pid]
            worst = cost(a.model, approx_tokens(p["text"]) * 2, MAX_OUTPUT_TOKENS)
            if run_spent + worst > a.budget or (a.model in BILLABLE and total + worst > TOTAL_BUDGET):
                print(f"stopped by the budget: USD {run_spent:.4f} spent in this run, "
                      f"USD {total:.4f} over all billable runs")
                break
            r = call(p["text"], p["case"], s)
            c = cost(a.model, r.input_tokens, r.output_tokens)
            run_spent += c
            total += c if a.model in BILLABLE else 0.0
            out.write(json.dumps({"model": a.model, "prompt_id": pid, "sample": s, "case": p["case"], "text": r.text,
                                  "input_tokens": r.input_tokens, "output_tokens": r.output_tokens,
                                  "stop": r.stop, "cost": c}) + "\n")
            out.flush()
    print(f"spent in this run: USD {run_spent:.4f} (prices USD {price_in}/{price_out} per million)")


def judge_and_report(a, conds, cases, conditions, prompts, folder, replies_path):
    """Judge every reply of these prompts, with a cache per case and code, and write the results."""
    replies = {(r["prompt_id"], r["sample"]): r for r in read_jsonl(replies_path) if r["prompt_id"] in prompts}
    cache_path = os.path.join(folder, "judged.jsonl")
    cache = {(j["case"], j["code_hash"]): j for j in read_jsonl(cache_path)}
    libraries = {cid: conds.errors[cid]["library"] for cid in cases}
    olds = {cid: conds.program(cid) for cid in cases}

    def key(r):
        code = extract(r["text"] or "")
        return r["case"], hashlib.sha256((code if code is not None else "\0none").encode()).hexdigest()[:16]

    pending = {}
    for r in replies.values():
        k = key(r)
        if k not in cache and k not in pending:
            pending[k] = r
    with ThreadPoolExecutor(a.workers) as pool:
        results = list(pool.map(lambda r: judge(a.envs, r["case"], libraries[r["case"]], r["text"],
                                                olds[r["case"]]), pending.values()))
    with open(cache_path, "a", encoding="utf-8") as f:
        for k, j in zip(pending, results):
            j = {"case": k[0], "code_hash": k[1], **{x: j[x] for x in j if x != "code"}}
            cache[k] = j
            f.write(json.dumps(j) + "\n")

    rows = []
    for pid, p in prompts.items():
        for s in range(a.samples):
            r = replies.get((pid, s))
            if r is None:
                continue
            j = cache[key(r)]
            for c in p["conditions"]:
                rows.append({"model": a.model, "case": p["case"], "condition": c, "template": a.template,
                             "sample": s, "prompt_id": pid, "shared": len(p["conditions"]),
                             "outcome": j["outcome"], "correct": j["correct"], "passes_test": j["passes_test"],
                             "violations": j["violations"], "warnings": j["warnings"],
                             "input_tokens": r["input_tokens"], "output_tokens": r["output_tokens"],
                             "stop": r["stop"], "error": j["error"].splitlines()[-1] if j["error"] else ""})
    rows.sort(key=lambda x: (x["case"][0] == "N", x["case"], ALL.index(x["condition"]), x["sample"]))
    with open(os.path.join(folder, "samples.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    by_cond = defaultdict(lambda: defaultdict(list))
    for x in rows:
        by_cond[x["condition"]][x["case"]].append(x["correct"])
    lines = [f"model {a.model}, template {a.template}, {len(rows)} sample rows",
             "condition  cases  pass@1 (mean over cases)"]
    for c in conditions:
        per_case = [sum(v) / len(v) for v in by_cond[c].values()]
        if per_case:
            lines.append(f"{c:9}  {len(per_case):5}  {sum(per_case) / len(per_case):.3f}")
    lines.append("outcomes (distinct samples): " + ", ".join(
        f"{k} {v}" for k, v in Counter(cache[key(r)]["outcome"] for r in replies.values()).most_common()))
    tokens_in = sum(r["input_tokens"] for r in replies.values())
    tokens_out = sum(r["output_tokens"] for r in replies.values())
    reasoning = sum(r.get("reasoning_tokens", 0) for r in replies.values())
    lines.append(f"tokens: {tokens_in:,} input, {tokens_out:,} output (of which {reasoning:,} reasoning); "
                 f"cost of these replies: USD {sum(r['cost'] for r in replies.values()):.4f}")
    gpu = sum(r.get("gpu_seconds", 0.0) for r in replies.values())
    if gpu:
        lines.append(f"GPU time of these replies: {gpu / 60:.1f} minutes")
    summary = "\n".join(lines)
    with open(os.path.join(folder, "summary.txt"), "w", encoding="utf-8") as f:
        f.write(summary + "\n")
    print(summary)


if __name__ == "__main__":
    main()
