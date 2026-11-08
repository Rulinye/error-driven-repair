"""Walk one test case through the pipeline of the study, step by step (Figure 1 of the thesis).

usage: measurements/envs/tools/bin/python demo/demo.py [--case P22] [--model qwen2.5-coder-7b]
                                                       [--no-pause] [--second]

Steps: the test case; the old program in the old and the new environment; the five error-message
conditions and the documentation conditions; the filled-in prompts; the model's replies; judging the
replies; and the results of the case. --second continues with P01, where a fix passes the test but
fails the validity checks.

Everything is computed live from the repository with the measurement environments in measurements/envs,
except the model replies, which are read from the replies recorded in the main runs
(runs/results/<model>/replies.jsonl). Each computed value is compared with the value stored by the
study's scripts.
"""
import argparse
import csv
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
for sub in ("runs", "conditions", "test_cases"):
    sys.path.insert(0, os.path.join(ROOT, sub))
from prompts import ALL, VERSIONS, Conditions, plan, prompt_id  # noqa: E402
from score import judge  # noqa: E402
from error_variants import correct_hint, failing_name, printed_error, run_case, strip_hint, with_sentence  # noqa: E402
from retrieval import BM25  # noqa: E402

ENVS = os.path.join(ROOT, "measurements", "envs")
CASES = os.path.join(ROOT, "test_cases", "cases")
RESULTS = os.path.join(ROOT, "runs", "results")
MODELS = ["gpt-6-luna", "gemini-3.8-flash", "qwen2.5-coder-7b", "codellama-7b"]
NAMES = {"gpt-6-luna": "GPT-6 Luna", "gemini-3.8-flash": "Gemini 3.8 Flash",
         "qwen2.5-coder-7b": "Qwen2.5-Coder-7B", "codellama-7b": "CodeLlama-7B"}
ENV_NAME = {"old": "pandas 1.5.3, NumPy 1.23.5", "mid": "pandas 2.2.3, NumPy 1.23.5", "new": "pandas 2.2.3, NumPy 2.1.3"}
COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
PAUSE = True


def c(text, code):
    return f"\033[{code}m{text}\033[0m" if COLOR else text


def bold(t):
    return c(t, "1")


def green(t):
    return c(t, "32")


def red(t):
    return c(t, "31")


def dim(t):
    return c(t, "2")


def step(n, total, title, note=""):
    if PAUSE:
        input(dim("\n  [Enter] "))
    print("\n" + c("=" * 100, "36"))
    print(c(f" STEP {n}/{total}  {title}", "1;36"))
    if note:
        print(dim(f" {note}"))
    print(c("=" * 100, "36"))


def block(text, prefix="  | ", limit=None):
    lines = text.rstrip("\n").splitlines()
    if limit and len(lines) > limit:
        lines = lines[:limit] + [f"... ({len(text.splitlines()) - limit} more lines)"]
    for line in lines:
        print(prefix + line)


def check(label, ok):
    print(f"  {label}: " + (green("yes") if ok else red("NO")))


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def run_visible(env, cid, program):
    """Run the test of a case with warnings shown; return the completed process."""
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "solution.py"), "w", encoding="utf-8") as f:
            f.write(program)
        shutil.copy(os.path.join(CASES, cid, "test.py"), os.path.join(tmp, "test.py"))
        p = subprocess.run([os.path.join(ENVS, env, "bin", "python"), "-W", "default", "test.py"], cwd=tmp,
                           capture_output=True, text=True, timeout=120)
        return p, tmp


def replies(model):
    with open(os.path.join(RESULTS, model, "replies.jsonl"), encoding="utf-8") as f:
        return {(r["prompt_id"], int(r["sample"])): r for r in map(json.loads, f) if r}


def walk(cid, model, total=9):
    conds = Conditions()
    case = {r["id"]: r for r in read(os.path.join(ROOT, "test_cases", "list.csv"))}[cid]
    stored = conds.errors[cid]
    library = case["library"]
    lib, old_v, new_v = VERSIONS[library]
    old_env, new_env = ("old", "mid") if library == "pandas" else ("mid", "new")
    program = conds.program(cid)

    # 1 ---------------------------------------------------------------------------------------------
    step(1, total, f"The test case {cid}", "test_cases/list.csv and test_cases/cases/" + cid)
    for k in ("library", "change_type", "old_usage", "replacement", "source"):
        print(f"  {k:12} {case[k]}")
    print(bold("\n  Old program (old.py), the code that the model sees:"))
    block("\n".join(f"{i + 1:3}  {line}" for i, line in enumerate(program.splitlines())))
    print(dim("\n  The test (test.py) checks the returned values; it is never shown to the model."))

    # 2 ---------------------------------------------------------------------------------------------
    step(2, total, f"Run the old program in the old environment ({lib} {old_v})",
         f"measurements/envs/{old_env}: {ENV_NAME[old_env]}, Python 3.11")
    p, tmp = run_visible(old_env, cid, program + "\n")
    print("  test result: " + (green(p.stdout.strip().splitlines()[-1]) if p.stdout.strip() else red("no output")))
    warnings = [line.replace(tmp, "<case>").strip() for line in p.stderr.splitlines() if "Warning" in line]
    if warnings:
        print(bold("  The old version warns:"))
        block("\n".join(warnings))

    # 3 ---------------------------------------------------------------------------------------------
    step(3, total, f"Run the same program in the new environment ({lib} {new_v})",
         f"measurements/envs/{new_env}: {ENV_NAME[new_env]}, Python 3.11")
    q = run_case(new_env, cid, program + "\n")
    print(red("  the program fails. End of the traceback:"))
    block(q.stderr.replace(q.tmp, "<case>").replace(os.path.abspath(ENVS) + os.sep, "<envs>/"))
    e0 = printed_error(q)
    print(bold("\n  E0, the original error message (the exception text, without the stack frames):"))
    block(e0)
    check("  same as the stored E0 (conditions/results/error_conditions.csv)", e0 == stored["E0"])

    # 4 ---------------------------------------------------------------------------------------------
    step(4, total, "Build the five error-message conditions by rules (conditions/error_variants.py)",
         "No language model is involved: E0 is the real error; E1 to E4 are derived from it by fixed rules.")
    e2, dropped = strip_hint(e0, failing_name(e0))
    e3 = with_sentence(e2, correct_hint(case))
    rows = [("E0", "original message", e0, None),
            ("E1", "no error message", stored["E1"], None),
            ("E2", "hint removed", e2, stored["E2"]),
            ("E3", "correct hint added", e3, stored["E3"]),
            ("E4", "misleading hint added", stored["E4"], None)]
    for level, name, text, ref in rows:
        print(bold(f"\n  {level}  {name}"))
        block(text)
        if ref is not None:
            check("     recomputed now, same as stored", text == ref)
    print(dim(f"\n  E2 removed from E0: {'; '.join(dropped) if dropped else 'nothing (the message has no hint)'}"))
    print(dim(f"  E4 names the public name closest in spelling to '{stored['removed_name']}' "
              f"('{stored['e4_name']}'); a fix that follows it was checked: {stored['e4_check']}."))

    # 5 ---------------------------------------------------------------------------------------------
    step(5, total, "Build the documentation conditions (conditions/retrieval.py)",
         "D0 none; D1 the top three release-note entries found by BM25; D2 the correct entry; "
         "D3 the correct entry with two distractors.")
    corpus = [r for r in read(os.path.join(ROOT, "conditions", "results", "corpus.csv")) if r["library"] == library]
    bm25 = BM25([r["text"] for r in corpus])
    query = stored["failing_line"] + "\n" + e2
    top = [corpus[i]["id"] for i in bm25.top(query, 3)]
    stored_top = conds.retrieved[(cid, "E2")]
    correct = set(conds.docs[cid]["correct_chunks"].split())
    print(bold("  BM25 query under E2 = the failing line + the error text:"))
    block(query)
    print(bold(f"\n  D1: the three entries retrieved from the {len(corpus)} entries of the {lib} release notes:"))
    for k, i in enumerate(top, 1):
        mark = green("  <- the correct entry") if i in correct else ""
        print(f"  {k}. [{i}]{mark}")
        block(conds.chunks[i][:300] + ("..." if len(conds.chunks[i]) > 300 else ""), prefix="     ")
    check("  recomputed now, same as stored (conditions/results/retrieval.csv)",
          top == [stored_top["top1"], stored_top["top2"], stored_top["top3"]])
    print(bold("\n  D2: the release-note entry of the change, with the old version's warning:"))
    block(conds.docs[cid]["D2"])

    # 6 ---------------------------------------------------------------------------------------------
    step(6, total, "Fill the prompt template (runs/prompts.py)",
         "The template designed by the author (Appendix B) + the program + the error text + the documentation.")
    p_e2 = conds.prompt(cid, "E2D0")
    p_e3 = conds.prompt(cid, "E3D0")
    print(bold("  Prompt for E2·D0 (no hint, no documentation), exactly as sent to the model:"))
    block(p_e2, prefix="  > ")
    print(bold("\n  Prompt for E3·D0 differs only in the error line:"))
    for line in difflib.unified_diff(p_e2.splitlines(), p_e3.splitlines(), lineterm="", n=0):
        if line.startswith(("---", "+++", "@@")):
            continue
        print("  " + (red(line) if line.startswith("-") else green(line)))
    distinct = plan(conds, [cid], ALL)
    print(dim(f"\n  The 20 conditions of {cid} give {len(distinct)} distinct prompts; identical prompts are "
              "sampled once and shared."))
    rep = replies(model)
    for cond, text in (("E2D0", p_e2), ("E3D0", p_e3)):
        pid = prompt_id(text)
        n = sum(1 for s in range(5) if (pid, s) in rep)
        check(f"  prompt id of {cond} {pid} found in runs/results/{model}/replies.jsonl ({n} replies)", n == 5)

    # 7 ---------------------------------------------------------------------------------------------
    step(7, total, f"The model's replies ({NAMES[model]}, recorded in the main runs)",
         f"runs/results/{model}/replies.jsonl: five samples per prompt at temperature 0.2")
    for cond, text in (("E2D0", p_e2), ("E3D0", p_e3)):
        r = rep[(prompt_id(text), 0)]
        print(bold(f"\n  {cond[:2]}·{cond[2:]}, sample 1 of 5:"))
        block(r["text"] or "", prefix="  < ", limit=30)

    # 8 ---------------------------------------------------------------------------------------------
    step(8, total, "Judge every reply (runs/score.py)",
         f"First code block -> hidden test in {lib} {new_v} -> validity checks (test_cases/validity.py)")
    recorded = {(r["condition"], int(r["sample"])): r["outcome"] for r in read(os.path.join(RESULTS, model, "samples.csv"))
                if r["case"] == cid and r["template"] == "main"}
    for cond, text in (("E2D0", p_e2), ("E3D0", p_e3)):
        print(bold(f"\n  {cond[:2]}·{cond[2:]}"))
        ok = 0
        for s in range(5):
            j = judge(ENVS, cid, library, rep[(prompt_id(text), s)]["text"], program + "\n")
            ok += j["correct"]
            line = green("correct") if j["correct"] else red(j["outcome"])
            why = j["error"].strip().splitlines()[-1][:90] if j["error"] else j["violations"]
            same = j["outcome"] == recorded[(cond, s)]
            print(f"  sample {s + 1}: {line}  {dim(why)}  {dim('(same as recorded)' if same else '(DIFFERS from recorded)')}")
            if s == 0 and j["code"]:
                for d in difflib.unified_diff(program.splitlines(), j["code"].rstrip("\n").splitlines(), lineterm="", n=0):
                    if not d.startswith(("---", "+++", "@@")):
                        print("      " + (red(d) if d.startswith("-") else green(d)))
        print(bold(f"  pass@1 under {cond[:2]}·{cond[2:]}: {ok}/5 = {ok / 5:.1f}"))

    # 9 ---------------------------------------------------------------------------------------------
    step(9, total, f"From one test case to the results", "runs/results/<model>/samples.csv and analysis/primary.txt")
    shown = ["E0D0", "E1D0", "E2D0", "E3D0", "E4D0", "E2D1", "E2D2", "E2D3", "E3D2", "E4D2"]
    print(bold(f"  Correct samples of {cid} (of 5) per model and condition:"))
    print("  " + " " * 18 + "".join(f"{x[:2] + '·' + x[2:]:>7}" for x in shown))
    for m in MODELS:
        cnt = defaultdict(int)
        for r in read(os.path.join(RESULTS, m, "samples.csv")):
            if r["case"] == cid and r["template"] == "main" and r["correct"] == "True":
                cnt[r["condition"]] += 1
        print(f"  {NAMES[m]:18}" + "".join(f"{cnt[x]:>7}" for x in shown))
    text = open(os.path.join(ROOT, "analysis", "primary.txt"), encoding="utf-8").read()
    part = text[text.index(NAMES[model] + "\n"):].split("\n\n")[0]
    print(bold(f"\n  Over all 90 test cases ({NAMES[model]}, analysis/primary.txt):"))
    block(part, prefix="  ")
    print(dim("\n  pass@1 is the mean over the 90 test cases; C1 = E3·D0 − E2·D0, computed within each test case."))


def second(total=3):
    cid, model = "P01", "codellama-7b"
    conds = Conditions()
    program = conds.program(cid)
    step(1, total, "Second example: P01, DataFrame.append", "The interpreter's suggestion in E0 points to a private method.")
    print(bold("  E0:"))
    block(conds.errors[cid]["E0"])
    print(bold("\n  Prompt E0·D0 for CodeLlama-7B, sample 3 of 5 (recorded):"))
    text = conds.prompt(cid, "E0D0")
    rep = replies(model)[(prompt_id(text), 2)]
    block(rep["text"], prefix="  < ", limit=25)
    step(2, total, "Judge it (runs/score.py)")
    j = judge(ENVS, cid, "pandas", rep["text"], program + "\n")
    print("  passes the test: " + (green("yes") if j["passes_test"] else red("no")))
    print("  validity checks: " + red(j["violations"] or "none"))
    print("  outcome: " + (green("correct") if j["correct"] else red(j["outcome"])))
    step(3, total, "Why the validity checks exist")
    print("  The fix calls the undocumented private method `_append`, which the interpreter suggested.")
    print("  It passes the test, but it is not a migration to the public API (pandas.concat), so it is")
    print("  counted as a failure (Section 3.9). In all main runs, only two fixes were rejected this way.")


def main():
    global PAUSE
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default="P22")
    ap.add_argument("--model", default="qwen2.5-coder-7b", choices=MODELS)
    ap.add_argument("--no-pause", action="store_true")
    ap.add_argument("--second", action="store_true", help="continue with P01 (validity checks)")
    a = ap.parse_args()
    PAUSE = not a.no_pause
    print(bold("\nError-driven code repair for Python library upgrades: one test case through the pipeline"))
    print(dim("All steps run live on this computer; the model replies are those recorded in the main runs."))
    walk(a.case, a.model)
    if a.second:
        second()
    print()


if __name__ == "__main__":
    main()
