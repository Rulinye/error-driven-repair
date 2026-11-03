"""Second test cases for the replication subset (Sections 3.2.3 and 4.6): admission checks and conditions.

usage: python test_cases/build_second.py
Run from the repository root after `bash measurements/run_all.sh` has built the environments.

The 30 changes were drawn with random.Random(SECOND_SEED).sample of the 90 test cases (in the order of
runs/prompts.py); see test_cases/README.md. Each has a second case in test_cases/second/<id>b/, written
separately in a different program context, with the files of test_cases/cases/.

For each second case, this script runs the admission checks of check_cases.py (with the leakage scan for the
change), and builds the error and documentation conditions with the code of conditions/error_variants.py and
conditions/retrieval.py: E0, the failing line and E4 come from the second program; E1 and E3 belong to the
change and are built the same way; D2 and the correct chunks are those of the change
(conditions/results/documentation.csv); D1 and the distractors of D3 are retrieved for the second program.
Writes test_cases/second/results/checks.csv, error_conditions.csv, documentation.csv and retrieval.csv.
"""
import csv
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
SECOND = os.path.join(HERE, "second")
RESULTS = os.path.join(SECOND, "results")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "probe"))
sys.path.insert(0, os.path.join(ROOT, "conditions"))
import error_variants as ev  # noqa: E402
from check_cases import run  # noqa: E402
from questions import REVIEW, matches  # noqa: E402
from retrieval import BM25, LEVELS, SEED  # noqa: E402
from validity import check  # noqa: E402

SECOND_SEED = 20261104
SUBSET = ["P01", "P03", "P04", "P11", "P16", "P24", "P31", "P32", "P34", "P35", "P36", "P37", "P40", "P41", "P42",
          "P45", "P47", "P62", "P63", "P64", "N04", "N05", "N07", "N10", "N15", "N16", "N17", "N22", "N28", "N33"]
# The second programs edited as the misleading hint of a behavior change says
E4_EDIT = {
    "P45b": [('sales.groupby("region").median()', 'sales.groupby("region", sort=False).median()')],
    "P47b": [('pd.to_datetime(invoices["due"])', 'pd.to_datetime(invoices["due"], utc=False)')],
}


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    sys.path.insert(0, os.path.join(ROOT, "runs"))
    from prompts import Conditions
    drawn = sorted(random.Random(SECOND_SEED).sample(Conditions().cases, 30), key=lambda c: (c[0] == "N", c))
    assert drawn == sorted(SUBSET, key=lambda c: (c[0] == "N", c)), drawn
    ev.CASES = SECOND  # error_variants runs the test of the case folder it is given
    cases = {r["id"]: r for r in read(os.path.join(HERE, "list.csv"))}
    first_docs = {r["id"]: r for r in read(os.path.join(ROOT, "conditions", "results", "documentation.csv"))}
    corpus = read(os.path.join(ROOT, "conditions", "results", "corpus.csv"))
    index = {lib: [c for c in corpus if c["library"] == lib] for lib in ("pandas", "NumPy")}
    bm25 = {lib: BM25([c["text"] for c in index[lib]]) for lib in index}
    py = {e: ev.python(e) for e in ("old", "mid", "new")}

    checks, errors, docs, runs = [], [], [], []
    for base in SUBSET:
        cid = base + "b"
        d = os.path.join(SECOND, cid)
        meta = json.load(open(os.path.join(d, "meta.json"), encoding="utf-8"))
        assert meta["id"] == cid and meta["change"] == base
        case = dict(cases[base], id=base)
        lib = case["library"]
        old_env, new_env = ev.envs_of(lib)
        program = open(os.path.join(d, "old.py"), encoding="utf-8").read()
        fixed = open(os.path.join(d, "fixed.py"), encoding="utf-8").read()

        # admission checks
        c1 = run(py[old_env], d, "old.py")[0]
        c2_pass, error, _ = run(py[new_env], d, "old.py")
        c2 = not c2_pass and not error.startswith("AssertionError")
        c3, fix_error, _ = run(py[new_env], d, "fixed.py")
        wrong = "none"
        if os.path.exists(os.path.join(d, "wrong.py")):
            wrong_code = open(os.path.join(d, "wrong.py"), encoding="utf-8").read()
            if not run(py[new_env], d, "wrong.py")[0]:
                wrong = "caught by the test"
            elif check(wrong_code, program):
                wrong = "caught by the validity checks"
            else:
                wrong = "NOT caught"
        leak = "by hand" if base in REVIEW else ("yes" if matches(base, program) else "no")
        invalid = check(fixed, program)
        admitted = c1 and c2 and c3 and wrong != "NOT caught" and leak != "yes" and not invalid

        # error conditions (as in error_variants.main, for the second program)
        e0 = ev.printed_error(ev.run_case(new_env, cid, program))
        name = ev.failing_name(e0)
        e1 = f"The code fails after upgrading {lib} from {ev.VERSIONS[lib][0]} to {ev.VERSIONS[lib][1]}."
        e2, dropped = ev.strip_hint(e0, name)
        e3 = ev.with_sentence(e2, ev.correct_hint(case))
        is_param = base in ev.PARAM_TARGET
        attr_target = next((v for k, v in ev.ATTR_TARGET.items() if k in e0), None) if not is_param else None
        spec = json.dumps({"attr_target": attr_target, "param_target": ev.PARAM_TARGET.get(base)})
        info = json.loads(ev.run_case(new_env, cid, program, spec).stdout.strip().splitlines()[-1])
        e4_name, e4_check, e4 = "", "", ""
        if base in ev.BEHAVIOR:
            edited = program
            for old_text, new_text in E4_EDIT[cid]:
                assert edited.count(old_text) == 1, (cid, old_text)
                edited = edited.replace(old_text, new_text)
            e4 = ev.with_sentence(e2, ev.BEHAVIOR[base][1])
            e4_check = ev.e4_outcome(new_env, cid, edited, program) or "passes (hint to be rewritten)"
        else:
            candidates = info["params"] if is_param else (info["obj_dir"] or [])
            for cand in ev.ranked(name, candidates, ev.fix_names(case)):
                result = ev.e4_outcome(new_env, cid, ev.substitute(program, name, cand, is_param), program)
                if result:
                    e4_name, e4_check = cand, result
                    break
            e4 = ev.with_sentence(e2, f"Did you mean: '{e4_name}'?") if e4_name else ""
        errors.append({"id": cid, "library": lib, "failing_line": info["line"], "removed_name": name,
                       "E0": e0, "E1": e1, "E2": e2, "E3": e3, "E4": e4, "e4_name": e4_name, "e4_check": e4_check,
                       "e2_dropped": " | ".join(dropped), "e0_equals_e2": "yes" if e0 == e2 else ""})

        # documentation conditions: D2 of the change, retrieval for the second program
        fd = first_docs[base]
        correct = set(fd["correct_chunks"].split())
        ranked = bm25[lib].top(info["line"] + "\n" + e2, len(index[lib]))
        distractors = [index[lib][i]["id"] for i in ranked if index[lib][i]["id"] not in correct][:2]
        order = ["D2"] + distractors
        random.Random(f"{SEED}-{cid}").shuffle(order)
        docs.append({"id": cid, "library": lib, "recorded_chunks": fd["recorded_chunks"],
                     "correct_chunks": fd["correct_chunks"], "D2": fd["D2"], "entry_names_fix": fd["entry_names_fix"],
                     "d2_names_fix": fd["d2_names_fix"], "D3_order": " ".join(order), "old_warnings": fd["old_warnings"]})
        texts = {"E0": e0, "E2": e2, "E3": e3, "E4": e4}
        for level in LEVELS:
            query = program if level == "E1" else info["line"] + "\n" + texts[level]
            top = [index[lib][i]["id"] for i in bm25[lib].top(query, 3)]
            runs.append({"id": cid, "level": level, "top1": top[0], "top2": top[1], "top3": top[2],
                         "recall_at_3": "yes" if set(top) & correct else "no"})
        checks.append({"id": cid, "library": lib, "old_passes_in_old": c1, "old_fails_in_new": c2,
                       "fix_passes_in_new": c3, "wrong_fix": wrong, "leak": leak,
                       "fix_validity": "; ".join(invalid) or "valid", "admitted": admitted,
                       "failing_line": info["line"], "error": error, "fix_error": "" if c3 else fix_error})
        print(f"{'ok ' if admitted else '-- '}{cid:5} wrong={wrong:20} leak={leak:7} E4={e4_name or '(by hand)':22} "
              f"{e4_check:26} | {info['line'][:50]}", flush=True)

    write(os.path.join(RESULTS, "checks.csv"), checks)
    write(os.path.join(RESULTS, "error_conditions.csv"), errors)
    write(os.path.join(RESULTS, "documentation.csv"), docs)
    write(os.path.join(RESULTS, "retrieval.csv"), runs)
    recall = {lv: sum(r["recall_at_3"] == "yes" for r in runs if r["level"] == lv) for lv in LEVELS}
    print(f"admitted {sum(c['admitted'] for c in checks)} of {len(checks)}; E0 equals E2 for "
          f"{sum(1 for e in errors if e['e0_equals_e2'])}; recall@3 " + ", ".join(f"{k} {v}" for k, v in recall.items()))


if __name__ == "__main__":
    main()
