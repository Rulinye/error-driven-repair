"""Build the 15 synthetic test cases: admission checks, error and documentation conditions, probe questions.

usage: python synthetic/build.py
Run from the repository root after `bash measurements/run_all.sh` has built the environments. Writes
synthetic/list.csv and, in synthetic/results/, checks.csv, error_conditions.csv, corpus.csv,
documentation.csv, retrieval.csv and questions.csv, in the formats of test_cases/ and conditions/ (Sections
3.2.3, 3.2.5, 3.4, 3.5 and 3.8).

The packages are pure Python and are put on the path of the Python 3.11 environment of measurements/: the
old version (packages/<library>/<old>/) for the old environment and the new version for the new one.

Admission checks, as in test_cases/check_cases.py: old.py passes its test with the old version and fails
with the new one (not with an AssertionError), fixed.py passes with the new version, wrong.py (if any)
fails the test or the validity checks, old.py does not contain the fix as the probe matches it, and
fixed.py passes the validity checks.

Error conditions, as in conditions/error_variants.py: E0 is what Python 3.11 prints for the error of old.py
with the new version; E2 drops the interpreter's suggestion and the sentences of the library's message that
contain a suggestion phrase or name another API; E3 adds "Use X instead."; E4 adds "Did you mean: 'Y'?" with
the public attribute or parameter closest to the removed name under the interpreter's distance measure,
without its cutoff and without the names of the fix, checked to fail the test or the validity checks.

Documentation conditions, as in conditions/retrieval.py: the corpus of a library is its release note, one
chunk per entry; D2 is the entry of the change; D1 the top three chunks by BM25 for the failing line and the
error text of the condition (the program under E1); D3 is D2 with the two highest-ranked other chunks for the
failing line and E2, in random order; recall@3 is whether the entry is among the top three.
"""
import csv
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
CASES = os.path.join(HERE, "cases")
PACKAGES = os.path.join(HERE, "packages")
NOTES = os.path.join(HERE, "release_notes")
RESULTS = os.path.join(HERE, "results")
PYTHON = os.path.join(ROOT, "measurements", "envs", "new", "bin", "python")
sys.path.insert(0, os.path.join(ROOT, "conditions"))
sys.path.insert(0, os.path.join(ROOT, "test_cases"))
sys.path.insert(0, os.path.join(ROOT, "probe"))
from error_variants import HINT, levenshtein, substitute, with_sentence  # noqa: E402
from questions import pattern  # noqa: E402
from retrieval import BM25, LEVELS, SEED, tokens  # noqa: E402
from validity import check  # noqa: E402

VERSIONS = {"fernledger": ("1.6.0", "2.0.0"), "gridwell": ("0.9.4", "1.0.0"), "quillery": ("3.2.1", "4.0.0")}
TIMEOUT = 60

# id: ("api", old API, fix) | ("param", parameter, function, fix); the fix as in probe/questions.py
SPEC = {
    "S01": ("api", "fernledger.parse_entries", [["read_journal"]]),
    "S02": ("api", "fernledger.Ledger.tally", [["bucketize"]]),
    "S03": ("param", "start", "fernledger.Ledger.running_total", [["opening"]]),
    "S04": ("param", "thousands", "fernledger.fmt_amount", [["style", "grouped"]]),
    "S05": ("api", "fernledger.merge", [["chain"]]),
    "S06": ("api", "gridwell.row_means", [["collapse", "mean"]]),
    "S07": ("api", "gridwell.Grid.neighbors", [["ring"]]),
    "S08": ("param", "wrap", "gridwell.smooth", [["boundary", "periodic"]]),
    "S09": ("api", "gridwell.peak_index", [["locate"]]),
    "S10": ("param", "reps", "gridwell.tile", [["layout"]]),
    "S11": ("api", "quillery.slugify", [["to_handle"]]),
    "S12": ("api", "quillery.Tokenizer.words", [["scan"]]),
    "S13": ("param", "width", "quillery.wrap", [["measure"]]),
    "S14": ("param", "strip_accents", "quillery.normalize", [["fold", "ascii"]]),
    "S15": ("api", "quillery.word_count", [["digest", "words"]]),
}
# Object whose public attributes are the E4 candidates of a removed API (the library's own message does not
# carry the object), and the release-note entry (1-5) of each change, in the order of the notes
ATTR_TARGET = {"S01": "fernledger", "S02": "fernledger.Ledger([])", "S05": "fernledger", "S06": "gridwell",
               "S07": "gridwell.Grid([[0]])", "S09": "gridwell", "S11": "quillery", "S12": "quillery.Tokenizer()",
               "S15": "quillery"}
ENTRY = {"S01": 1, "S02": 3, "S03": 4, "S04": 5, "S05": 2, "S06": 1, "S07": 3, "S08": 4, "S09": 2, "S10": 5,
         "S11": 1, "S12": 3, "S13": 4, "S14": 5, "S15": 2}

PROBE = r"""
import inspect, json, runpy, sys, traceback
spec = json.loads(sys.argv[1])
out = {"line": "", "obj_dir": None, "params": None}
try:
    runpy.run_path("test.py", run_name="__main__")
except BaseException as e:
    frames = [f for f in traceback.extract_tb(e.__traceback__) if f.filename.endswith("solution.py")]
    if frames:
        out["line"] = (frames[-1].line or "").strip()
import importlib
mod = importlib.import_module(spec["library"])
ns = {spec["library"]: mod}
if spec.get("attr_target"):
    out["obj_dir"] = sorted(dir(eval(spec["attr_target"], ns)))
if spec.get("param_target"):
    sig = inspect.signature(eval(spec["param_target"], ns))
    out["params"] = [p.name for p in sig.parameters.values()
                     if p.name != "self" and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)]
print(json.dumps(out))
"""


def package_path(library, which):
    return os.path.join(PACKAGES, library, VERSIONS[library][0 if which == "old" else 1])


def run(cid, library, which, program, probe=None):
    """Run the test of a case on a program with the old or new version of the package."""
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "solution.py"), "w", encoding="utf-8") as f:
            f.write(program)
        shutil.copy(os.path.join(CASES, cid, "test.py"), os.path.join(tmp, "test.py"))
        env = dict(os.environ, PYTHONPATH=package_path(library, which))
        cmd = [PYTHON, "-W", "ignore"] + (["-c", PROBE, probe] if probe else ["test.py"])
        p = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True, timeout=TIMEOUT, env=env)
        p.tmp = tmp
        return p


def passes(p):
    return p.returncode == 0 and p.stdout.strip().endswith("PASS")


def printed_error(p):
    """The exception text the interpreter prints for the uncaught error (no stack frames)."""
    if "Traceback (most recent call last):" not in p.stderr:
        return ""
    block = p.stderr.rsplit("Traceback (most recent call last):", 1)[1].splitlines()[1:]
    i = 0
    while i < len(block) and (block[i].startswith("  ") or not block[i].strip()):
        i += 1
    return "\n".join(block[i:]).strip().replace(p.tmp, "<case>")


def failing_name(e0):
    for pat in (r"has no attribute '(\w+)'", r"unexpected keyword argument '(\w+)'", r"`\w+\.(\w+)` was removed"):
        m = re.search(pat, e0)
        if m:
            return m.group(1)
    return ""


def strip_hint(e0, library, name):
    """E2: drop the interpreter's suggestion and the sentences with a suggestion phrase or another API."""
    text = re.sub(r"\.? Did you mean:? '?[^'?]+'?\?\s*$", "", e0.strip())
    head, _, msg = text.partition(": ")
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z`'])", msg)
    allowed = {name, f"{library}.{name}"}
    kept, dropped = [], []
    for s in sentences:
        others = [n for n in re.findall(r"`([^`]+)`", s) if n not in allowed]
        (dropped if HINT.search(s) or others else kept).append(s)
    e2 = head + ": " + " ".join(kept) if kept else head
    return e2.rstrip(), dropped


def matches(cid, text):
    return any(all(pattern(p).search(text) for p in alt) for alt in SPEC[cid][-1])


def fix_names(cid, meta):
    ident = r"[A-Za-z_]\w*"
    names = set(re.findall(ident, meta["replacement"])) - set(re.findall(ident, meta["old_usage"]))
    return names | {p for alt in SPEC[cid][-1] for p in alt}


def ranked(name, candidates, exclude):
    pool = [c for c in candidates if not c.startswith("_") and c != name and c not in exclude]
    return sorted(pool, key=lambda c: levenshtein(name, c))


def question(cid, library):
    kind, *fields = SPEC[cid]
    lib = f"{library} {VERSIONS[library][1]}"
    if kind == "api":
        return f"In {lib}, {fields[0]} was removed. What should be used instead?"
    return (f"In {lib}, the parameter {fields[0]} of {fields[1]} was removed. "
            "How should a call that uses it be changed?")


def chunks(library):
    """[(line, section, text)]: one chunk per bullet entry of the release note."""
    fname = f"{library}_{VERSIONS[library][1]}.md"
    out, section = [], ""
    for n, line in enumerate(open(os.path.join(NOTES, fname), encoding="utf-8").read().splitlines(), 1):
        if line.startswith("## "):
            section = line[3:].strip()
        elif line.startswith("- "):
            out.append((n, section, line[2:].strip()))
    return fname, out


def write(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    ids = sorted(d for d in os.listdir(CASES) if os.path.isdir(os.path.join(CASES, d)))
    assert ids == sorted(SPEC), ids
    metas = {cid: json.load(open(os.path.join(CASES, cid, "meta.json"), encoding="utf-8")) for cid in ids}

    corpus = []
    for lib in VERSIONS:
        fname, cs = chunks(lib)
        assert len(cs) == 8, (lib, len(cs))
        for line, section, text in cs:
            corpus.append({"id": f"{fname[:-3]}:L{line}", "library": lib, "file": fname, "line": line,
                           "section": section, "entry": "", "text": text})
    index = {lib: [c for c in corpus if c["library"] == lib] for lib in VERSIONS}
    bm25 = {lib: BM25([c["text"] for c in index[lib]]) for lib in VERSIONS}

    listing, checks, errors, docs, runs, questions = [], [], [], [], [], []
    for cid in ids:
        meta, lib = metas[cid], metas[cid]["library"]
        read = lambda name: open(os.path.join(CASES, cid, name), encoding="utf-8").read()  # noqa: E731
        old, fixed = read("old.py"), read("fixed.py")
        wrong = read("wrong.py") if os.path.exists(os.path.join(CASES, cid, "wrong.py")) else None

        # admission checks
        c1 = passes(run(cid, lib, "old", old))
        p2 = run(cid, lib, "new", old)
        e0 = printed_error(p2)
        c2 = not passes(p2) and bool(e0) and not e0.startswith("AssertionError")
        p3 = run(cid, lib, "new", fixed)
        c3 = passes(p3)
        wrong_result = "none"
        if wrong is not None:
            if not passes(run(cid, lib, "new", wrong)):
                wrong_result = "caught by the test"
            elif check(wrong, old):
                wrong_result = "caught by the validity checks"
            else:
                wrong_result = "NOT caught"
        leak = "yes" if matches(cid, old) else "no"
        invalid = check(fixed, old)
        admitted = c1 and c2 and c3 and wrong_result != "NOT caught" and leak == "no" and not invalid

        # error conditions
        name = failing_name(e0)
        old_v, new_v = VERSIONS[lib]
        e1 = f"The code fails after upgrading {lib} from {old_v} to {new_v}."
        e2, dropped = strip_hint(e0, lib, name)
        e3 = with_sentence(e2, f"Use `{meta['replacement']}` instead.")
        kind = SPEC[cid][0]
        spec = {"library": lib, "attr_target": ATTR_TARGET.get(cid),
                "param_target": SPEC[cid][2] if kind == "param" else None}
        info = json.loads(run(cid, lib, "new", old, json.dumps(spec)).stdout.strip().splitlines()[-1])
        candidates = info["params"] if kind == "param" else info["obj_dir"]
        e4_name, e4_check = "", ""
        for cand in ranked(name, candidates, fix_names(cid, meta)):
            program = substitute(old, name, cand, kind == "param")
            if program == old:
                continue
            if not passes(run(cid, lib, "new", program)):
                e4_name, e4_check = cand, "fails the test"
            elif check(program, old):
                e4_name, e4_check = cand, "fails the validity checks"
            if e4_name:
                break
        e4 = with_sentence(e2, f"Did you mean: '{e4_name}'?") if e4_name else ""

        # documentation conditions
        entry_chunk = [c for c in index[lib] if c["section"] == index[lib][0]["section"]][ENTRY[cid] - 1]
        d2 = entry_chunk["text"]
        ranked_ids = [index[lib][i]["id"] for i in bm25[lib].top(info["line"] + "\n" + e2, len(index[lib]))]
        distractors = [i for i in ranked_ids if i != entry_chunk["id"]][:2]
        order = ["D2"] + distractors
        random.Random(f"{SEED}-{cid}").shuffle(order)
        hint_names = {t for n in re.findall(r"`([^`]+)`", e3[len(e2):]) for t in tokens(n) if len(t) > 2}
        docs.append({"id": cid, "library": lib, "recorded_chunks": entry_chunk["id"],
                     "correct_chunks": entry_chunk["id"], "D2": d2, "entry_names_fix": "yes",
                     "d2_names_fix": "yes" if hint_names & set(tokens(d2)) else "no",
                     "D3_order": " ".join(order), "old_warnings": ""})
        for level in LEVELS:
            text = {"E0": e0, "E2": e2, "E3": e3, "E4": e4}.get(level)
            query = old if level == "E1" else info["line"] + "\n" + text
            top = [index[lib][i]["id"] for i in bm25[lib].top(query, 3)]
            runs.append({"id": cid, "level": level, "top1": top[0], "top2": top[1], "top3": top[2],
                         "recall_at_3": "yes" if entry_chunk["id"] in top else "no"})

        listing.append({"id": cid, "library": lib, "old_version": old_v, "new_version": new_v,
                        "change_type": meta["change_type"], "old_usage": meta["old_usage"],
                        "replacement": meta["replacement"], "source": meta["source"]})
        checks.append({"id": cid, "library": lib, "old_passes_in_old": c1, "old_fails_in_new": c2,
                       "fix_passes_in_new": c3, "wrong_fix": wrong_result, "leak": leak,
                       "fix_validity": "; ".join(invalid) or "valid", "admitted": admitted,
                       "failing_line": info["line"], "error": e0, "fix_error": "" if c3 else printed_error(p3)})
        errors.append({"id": cid, "library": lib, "failing_line": info["line"], "removed_name": name,
                       "E0": e0, "E1": e1, "E2": e2, "E3": e3, "E4": e4, "e4_name": e4_name, "e4_check": e4_check,
                       "e2_dropped": " | ".join(dropped), "e0_equals_e2": "yes" if e0 == e2 else ""})
        questions.append({"id": cid, "library": lib, "change_type": meta["change_type"],
                          "question": question(cid, lib), "recorded_fix": meta["replacement"],
                          "checked_by_hand": "unclear answers"})
        print(f"{'ok ' if admitted else '-- '}{cid}  1={c1!s:5} 2={c2!s:5} 3={c3!s:5} wrong={wrong_result:29} "
              f"leak={leak:3} E4={e4_name or '-':12} | {e0[:70]}", flush=True)

    write(os.path.join(HERE, "list.csv"), listing)
    write(os.path.join(RESULTS, "checks.csv"), checks)
    write(os.path.join(RESULTS, "error_conditions.csv"), errors)
    write(os.path.join(RESULTS, "corpus.csv"), corpus)
    write(os.path.join(RESULTS, "documentation.csv"), docs)
    write(os.path.join(RESULTS, "retrieval.csv"), runs)
    write(os.path.join(RESULTS, "questions.csv"), questions)
    recall = {lv: sum(r["recall_at_3"] == "yes" for r in runs if r["level"] == lv) for lv in LEVELS}
    print(f"admitted {sum(c['admitted'] for c in checks)} of {len(checks)}; E0 equals E2 for "
          f"{sum(1 for e in errors if e['e0_equals_e2'])}; recall@3 " + ", ".join(f"{k} {v}" for k, v in recall.items()))


if __name__ == "__main__":
    main()
