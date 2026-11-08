"""Post-hoc analyses (Section 6.8). They were added after a review of the draft and are not part of the frozen plan.

usage: python analysis/posthoc.py

Uses the stored replies and judgments of the main and synthetic runs; carries no tests. Writes posthoc.txt.
  1. Missing imports: failed fixes that only lack an import of pandas or NumPy are run again with the import added.
  2. Following the misleading hint: how many E4·D0 samples contain the misleading name, how many misleading names lie
     within the cutoff of the interpreter (Python 3.11), and C2 on those changes.
  3. Old warnings in D2: C3 and C4 for the test cases whose D2 contains the old version's warning and for the others.
  4. Truncated replies: C1 and C3 on unknown changes (H4) without the replies that have no code block.
  5. Shared release-note entries: the primary contrasts with the release-note entries as units.
  6. Random and hand-chosen changes: probe labels and E2·D0 for the 10 changes drawn at random and the other 80.
  7. Ruff with its unsafe fixes as well.
"""
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "runs"))
sys.path.insert(0, os.path.join(ROOT, "conditions"))
from inference import counts, signs, contrast, holm  # noqa: E402
from score import extract, run_test, check, judge, NEW_ENV  # noqa: E402
from error_variants import levenshtein, MOVE_COST  # noqa: E402
from ruff_baseline import ruff  # noqa: E402

RESULTS = os.path.join(ROOT, "runs", "results")
ENVS = os.path.join(ROOT, "measurements", "envs")
MODELS = ["gpt-6-luna", "gemini-3.8-flash", "qwen2.5-coder-7b", "codellama-7b"]
SEED = 20261102
C = {"C1": {"E3D0": 1, "E2D0": -1}, "C2": {"E4D0": 1, "E2D0": -1}, "C3": {"E2D2": 1, "E2D0": -1},
     "C4": {"E2D2": 1, "E2D0": -1, "E3D2": -1, "E3D0": 1}, "C5": {"E4D2": 1, "E4D0": -1, "E2D2": -1, "E2D0": 1}}
IMPORT = re.compile(r"NameError: name '(\w+)' is not defined")
ADD = {"pd": "import pandas as pd", "pandas": "import pandas", "np": "import numpy as np", "numpy": "import numpy",
       "functools": "import functools", "reduce": "from functools import reduce", "warnings": "import warnings"}


def read(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def samples(folder):
    return [r for r in read(os.path.join(RESULTS, folder, "samples.csv")) if r["template"] == "main"]


def replies(folder):
    with open(os.path.join(RESULTS, folder, "replies.jsonl"), encoding="utf-8") as f:
        return {(r["prompt_id"], str(r["sample"])): r for r in map(json.loads, f) if r}


def cells(rows, ok=lambda r: r["correct"] == "True", drop=None):
    out = defaultdict(list)
    for r in rows:
        if drop and drop(r):
            continue
        out[(r["case"], r["condition"])].append(ok(r))
    return out


def rate(c, k):
    v = c.get(k, [])
    return float(np.mean(v)) if v else np.nan


def ctr(c, ids, w):
    d = np.array([100 * sum(wt * rate(c, (i, k)) for k, wt in w.items()) for i in ids
                  if not any(np.isnan(rate(c, (i, k))) for k in w)])
    m, lo, hi, p = contrast(d, counts(len(d), seed=SEED), signs(len(d), seed=SEED + 1))
    return f"{m:+6.1f} [{lo:+6.1f}, {hi:+6.1f}] p={p:.4f} (n={len(d)})", m


def mean_rate(c, ids, cond):
    return 100 * np.nanmean([rate(c, (i, cond)) for i in ids])


errors = {r["id"]: r for r in read(os.path.join(ROOT, "conditions", "results", "error_conditions.csv"))}
docs = {r["id"]: r for r in read(os.path.join(ROOT, "conditions", "results", "documentation.csv"))}
lst = {r["id"]: r for r in read(os.path.join(ROOT, "test_cases", "list.csv"))}
known = {(r["model"], r["id"]): r["label"] for r in read(os.path.join(ROOT, "probe", "results", "known.csv"))}
known_syn = {(r["model"], r["id"]): r["label"] for r in read(os.path.join(ROOT, "synthetic", "results", "known.csv"))}
ids = sorted(errors, key=lambda c: (c[0] == "N", c))
main = {m: samples(m) for m in MODELS}
out = []


def say(s=""):
    print(s, flush=True)
    out.append(s)


# 1 ---------------------------------------------------------------------------------------------------
say("1. Missing imports (main runs): failed fixes that only lack an import, run again with the import added")


def rejudge(item):
    """True if the fix passes once the missing imports (at most three) are added."""
    (cid, _), (code, err) = item
    py = os.path.join(ENVS, NEW_ENV[errors[cid]["library"]], "bin", "python")
    old = open(os.path.join(ROOT, "test_cases", "cases", cid, "old.py"), encoding="utf-8").read()
    added = []
    for _ in range(3):
        m = IMPORT.search(err)
        if not m or m.group(1) not in ADD:
            return item[0], False
        added.append(ADD[m.group(1)])
        new = "\n".join(added) + "\n" + code
        ok, err, _ = run_test(py, cid, new)
        if ok:
            return item[0], not check(new, old)
    return item[0], False


for model in MODELS:
    reps = replies(model)
    todo, keyof = {}, {}
    for r in main[model]:
        m = IMPORT.search(r["error"])
        if r["outcome"] == "fails the test" and m and m.group(1) in ADD:
            code = extract(reps[(r["prompt_id"], r["sample"])]["text"] or "")
            k = (r["case"], hashlib.sha256(code.encode()).hexdigest()[:16])
            todo[k] = (code, r["error"])
            keyof[(r["prompt_id"], r["sample"])] = k
    with ThreadPoolExecutor(8) as pool:
        passed = dict(pool.map(rejudge, todo.items()))
    failed = {(r["prompt_id"], r["sample"]) for r in main[model] if r["correct"] != "True"}
    with_import = sum(1 for k in failed if k in keyof)
    a = cells(main[model])
    b = cells(main[model], ok=lambda r: r["correct"] == "True" or passed.get(keyof.get((r["prompt_id"], r["sample"])), False))
    say(f"  {model}: {with_import} of {len(failed)} distinct failed samples lack only an import, from {len(todo)} "
        f"distinct fixes; {sum(passed.values())} of these fixes pass with the import")
    say("    " + "  ".join(f"{c} {mean_rate(a, ids, c):.1f}->{mean_rate(b, ids, c):.1f}"
                           for c in ["E0D0", "E2D0", "E3D0", "E4D0", "E2D2"]))
    say("    " + "  ".join(f"{k} {ctr(a, ids, w)[1]:+.1f}->{ctr(b, ids, w)[1]:+.1f}" for k, w in C.items()))

# 2 ---------------------------------------------------------------------------------------------------
say("")
say("2. Following the misleading hint (E4 without documentation)")
named = [i for i in ids if errors[i]["e4_name"]]
within = [i for i in named if levenshtein(errors[i]["removed_name"], errors[i]["e4_name"])
          <= (len(errors[i]["removed_name"]) + len(errors[i]["e4_name"]) + 3) * MOVE_COST // 6]
say(f"  misleading hints that name a name: {len(named)}; within the interpreter's cutoff: {len(within)} ({' '.join(within)})")
for model in MODELS:
    reps = replies(model)
    seen, use, fail = set(), 0, 0
    for r in main[model]:
        key = (r["prompt_id"], r["sample"])
        if r["condition"] != "E4D0" or r["case"] not in named or key in seen:
            continue
        seen.add(key)
        code = extract(reps[key]["text"] or "") or ""
        old = open(os.path.join(ROOT, "test_cases", "cases", r["case"], "old.py"), encoding="utf-8").read()
        y = re.escape(errors[r["case"]]["e4_name"])
        if re.search(rf"\b{y}\b", code) and not re.search(rf"\b{y}\b", old):
            use += 1
            fail += r["correct"] != "True"
    a = cells(main[model])
    say(f"  {model}: {use} of {len(seen)} samples contain the misleading name, {fail} of them fail; "
        f"C2 within the cutoff {ctr(a, within, C['C2'])[0]}")

# 3 ---------------------------------------------------------------------------------------------------
say("")
warn = [i for i in ids if docs[i]["old_warnings"].strip()]
nowarn = [i for i in ids if i not in warn]
say(f"3. Old warnings in D2: {len(warn)} test cases with the warning, {len(nowarn)} without")
for model in MODELS:
    a = cells(main[model])
    for k in ("C3", "C4"):
        say(f"  {model} {k}: with {ctr(a, warn, C[k])[0]}   without {ctr(a, nowarn, C[k])[0]}")

# 4 ---------------------------------------------------------------------------------------------------
say("")
say("4. Truncated replies: H4 (C1, C3 on unknown changes) with all samples and without replies that have no code block")
for model in MODELS:
    syn = samples(model + "-synthetic")
    nb = Counter(r["condition"] for r in syn if r["outcome"] == "no code block")
    distinct = len({(r["prompt_id"], r["sample"]) for r in syn if r["outcome"] == "no code block"})
    rows = main[model] + syn
    unk = [i for i in ids if known[(model, i)] != "known"] + sorted(
        {r["case"] for r in syn if known_syn[(model, r["case"])] != "known"})
    a = cells(rows)
    b = cells(rows, drop=lambda r: r["outcome"] == "no code block")
    say(f"  {model}: {distinct} synthetic replies without a code block; by condition {dict(sorted(nb.items()))}")
    for k in ("C1", "C3"):
        say(f"    {k}: all {ctr(a, unk, C[k])[0]}   without them {ctr(b, unk, C[k])[0]}")

# 5 ---------------------------------------------------------------------------------------------------
say("")
groups = defaultdict(list)
for i in ids:
    groups[docs[i]["correct_chunks"]].append(i)
groups = list(groups.values())
say(f"5. Shared release-note entries: {len(groups)} entries as units (bootstrap and sign-flip over entries, Holm)")
R = 10000
draw = np.random.default_rng(SEED).integers(0, len(groups), size=(R, len(groups)))
flip = np.where(np.random.default_rng(SEED + 1).random((R, len(groups))) < 0.5, -1.0, 1.0)
for model in MODELS:
    a = cells(main[model])
    res = []
    for k, w in C.items():
        d = {i: 100 * sum(wt * rate(a, (i, kk)) for kk, wt in w.items()) for i in ids}
        sums = np.array([sum(d[i] for i in g) for g in groups])
        sizes = np.array([len(g) for g in groups])
        m = sums.sum() / sizes.sum()
        lo, hi = np.percentile(sums[draw].sum(1) / sizes[draw].sum(1), [2.5, 97.5])
        p = (1 + (np.abs((flip * sums).sum(1) / sizes.sum()) >= abs(m) - 1e-9).sum()) / (1 + R)
        res.append((k, m, lo, hi, p))
    ps = holm([x[4] for x in res])
    say(f"  {model}: " + "; ".join(f"{k} {m:+.1f} [{lo:+.1f}, {hi:+.1f}] p={q:.4f}" for (k, m, lo, hi, _), q in zip(res, ps)))

# 6 ---------------------------------------------------------------------------------------------------
say("")
rnd = [i for i in ids if lst[i]["origin"] == "drawn from the pool"]
hand = [i for i in ids if i not in rnd]
say(f"6. Random and hand-chosen changes: {len(rnd)} drawn ({' '.join(rnd)}), {len(hand)} chosen by hand")
for model in MODELS:
    a = cells(main[model])
    say(f"  {model}: known {sum(known[(model, i)] == 'known' for i in rnd)}/{len(rnd)} and "
        f"{sum(known[(model, i)] == 'known' for i in hand)}/{len(hand)}; E2D0 {mean_rate(a, rnd, 'E2D0'):.1f} and "
        f"{mean_rate(a, hand, 'E2D0'):.1f}")

# 7 ---------------------------------------------------------------------------------------------------
say("")
correct = 0
from prompts import Conditions  # noqa: E402
conds = Conditions()
for cid in conds.cases:
    old = conds.program(cid)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "solution.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(old)
        ruff(["--fix", "--unsafe-fixes"], path)
        fixed = open(path, encoding="utf-8").read()
    if fixed != old:
        correct += judge(ENVS, cid, errors[cid]["library"], f"```python\n{fixed}\n```", old)["correct"]
say(f"7. Ruff with its unsafe fixes as well: {correct} of {len(conds.cases)} test cases fixed")

with open(os.path.join(HERE, "posthoc.txt"), "w", encoding="utf-8") as f:
    f.write("Post-hoc analyses (Section 6.8); not part of the frozen plan.\n\n" + "\n".join(out) + "\n")
