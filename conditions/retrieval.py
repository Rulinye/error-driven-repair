"""Build the documentation conditions D1-D3 for every test case (Section 3.5).

usage: python conditions/retrieval.py
Reads screening/release_notes/*.rst, test_cases/list.csv, the programs in test_cases/cases/,
conditions/results/error_conditions.csv and screening/results/release_note_*.csv. Writes conditions/results/corpus.csv, documentation.csv and
retrieval.csv.

Corpus: for each library, the official release notes of every release between the two versions (pandas
2.0.0, 2.1.0, 2.2.0; NumPy 1.24.0, 1.25.0, 1.26.0, 2.0.0, 2.1.0) and, for NumPy, the NumPy 2.0 migration
guide, split into one chunk per bullet entry, per table row, or per paragraph. Headings, labels and
directive lines are not chunks; the content of a directive (for example a code example) is.

Retrieval: Okapi BM25 (k1 = 1.5, b = 0.75, idf = ln((N - n + 0.5) / (n + 0.5) + 1)) over lowercased tokens
of letters and digits; underscores, dots and other characters separate tokens.

  D1  the top three chunks for the query "failing line + error text of the current condition"; under E1,
      which has no error and so no failing line, the query is the complete program of the test case
  D2  the chunk of the recorded entry for the change, with the deprecation warning that the old version
      emits for the same call, if any
  D3  D2 together with the two highest-ranked incorrect chunks for "failing line + E2", in random order
recall@3 is whether a correct chunk is among the three retrieved. Correct chunks are the recorded entry
and the release-note entries that the screening found to describe the same removed name or parameter.
entry_names_fix records, by reading, whether the recorded entry itself names the fix; ENTRY_NO_FIX lists
the 21 test cases whose entry does not, and for each of them the old warning in D2 does. d2_names_fix
records whether D2 names the fix: whether an identifier of the correct hint (E3) occurs in D2; the 9
behavior changes, whose hint is a sentence, were decided by reading (all name it).
"""
import csv
import json
import math
import os
import random
import re
import subprocess
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
NOTES = os.path.join(ROOT, "screening", "release_notes")
ENVS = os.path.join(ROOT, "measurements", "envs")
HARNESS = os.path.join(ROOT, "measurements", "scripts", "harness.py")
SETUP = "import io, datetime, functools, numpy as np, pandas as pd\n"
FILES = {
    "pandas": ["pandas_2.0.0.rst", "pandas_2.1.0.rst", "pandas_2.2.0.rst"],
    "NumPy": ["numpy_1.24.0.rst", "numpy_1.25.0.rst", "numpy_1.26.0.rst", "numpy_2.0.0.rst", "numpy_2.1.0.rst",
              "numpy_2.0_migration_guide.rst"],
}
SOURCE_FILE = {"v2.0.0.rst": "pandas_2.0.0.rst", "1.24.0-notes.rst": "numpy_1.24.0.rst",
               "1.25.0-notes.rst": "numpy_1.25.0.rst", "2.0.0-notes.rst": "numpy_2.0.0.rst"}
GUIDE = "numpy_2.0_migration_guide.rst"
GUIDE_SECTION = {"Changes to data type promotion": "Changes to NumPy data type promotion"}
K1, B = 1.5, 0.75
SEED = 20261026
LEVELS = ["E0", "E1", "E2", "E3", "E4"]
# Test cases whose recorded entry does not name the fix, by reading; the old warning names it for each
# (P35: the entry's "Use offset or origin" applies to base, not to loffset; P33: the warning suggests a list
# comprehension on the column names; P38: the warning says that a new object is returned)
ENTRY_NO_FIX = {"P05", "P06", "P07", "P24", "P26", "P27", "P28", "P31", "P32", "P33", "P35", "P38", "P39",
                "P44", "P54", "P61", "P68", "N01", "N02", "N04", "N05"}
UNDERLINE = re.compile(r"^([-=~^*\"#+])\1{3,}\s*$")
TABLE_RULE = re.compile(r"^=+(\s+=+)+\s*$")


def clean(text):
    text = re.sub(r":\w+:`~?([^`<]+?)(?:\s*<[^>]+>)?`", r"\1", text)
    text = re.sub(r"`([^`<]+?)\s*<[^>]+>`__?", r"\1", text)
    text = re.sub(r"\(\s*:issue:`[^)]*\)|\(`gh-\d+[^)]*\)", "", text)
    text = text.replace("``", "`").replace("\\_", "_")
    return " ".join(text.split())


def chunks_of(fname):
    """[(line, section, text)] for one rst file."""
    lines = open(os.path.join(NOTES, fname), encoding="utf-8").read().splitlines()
    heads = {i for i in range(1, len(lines)) if UNDERLINE.match(lines[i]) and lines[i - 1].strip()
             and not UNDERLINE.match(lines[i - 1]) and not TABLE_RULE.match(lines[i])}
    out, section, i = [], "", 0
    while i < len(lines):
        line = lines[i]
        if i + 1 in heads:
            section = line.strip()
            i += 2
            continue
        if not line.strip() or UNDERLINE.match(line) and not TABLE_RULE.match(line):
            i += 1
            continue
        if TABLE_RULE.match(line):  # simple table: one chunk per row of the body
            rules, j, rows = 0, i, []
            while j < len(lines) and rules < 3:
                if TABLE_RULE.match(lines[j]):
                    rules += 1
                elif rules == 2 and lines[j].strip():
                    if lines[j][0] != " " or not rows:
                        rows.append([j + 1, lines[j].strip()])
                    else:
                        rows[-1][1] += " " + lines[j].strip()
                j += 1
            out += [(ln, section, clean(t)) for ln, t in rows]
            i = j
            continue
        if line.startswith(".. "):  # label or directive; its indented content is one chunk
            j, body = i + 1, []
            while j < len(lines) and (not lines[j].strip() or lines[j].startswith(" ")):
                if lines[j].strip() and not lines[j].strip().startswith(":"):
                    body.append(lines[j].strip())
                j += 1
            if body:
                out.append((i + 2, section, clean(" ".join(body))))
            i = j
            continue
        if re.match(r"^[-*] ", line):  # bullet with its continuation and nested bullets
            j, text = i + 1, [line[2:]]
            while j < len(lines) and lines[j].startswith(" ") and lines[j].strip():
                text.append(lines[j].strip())
                j += 1
            out.append((i + 1, section, clean(" ".join(text))))
            i = j
            continue
        j, text = i, []  # paragraph
        while j < len(lines) and lines[j].strip() and j + 1 not in heads and not TABLE_RULE.match(lines[j]) \
                and not lines[j].startswith(".. ") and not re.match(r"^[-*] ", lines[j]):
            text.append(lines[j].strip())
            j += 1
        out.append((i + 1, section, clean(" ".join(text))))
        i = max(j, i + 1)
    return [c for c in out if c[2]]


def tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())


class BM25:
    def __init__(self, docs):
        self.docs = [Counter(tokens(d)) for d in docs]
        self.len = [sum(d.values()) for d in self.docs]
        self.avg = sum(self.len) / len(self.len)
        df = Counter(t for d in self.docs for t in d)
        n = len(self.docs)
        self.idf = {t: math.log((n - k + 0.5) / (k + 0.5) + 1) for t, k in df.items()}

    def scores(self, query):
        q = tokens(query)
        out = []
        for d, length in zip(self.docs, self.len):
            s = 0.0
            for t in q:
                f = d.get(t, 0)
                if f:
                    s += self.idf[t] * f * (K1 + 1) / (f + K1 * (1 - B + B * length / self.avg))
            out.append(s)
        return out

    def top(self, query, k):
        s = self.scores(query)
        return sorted(range(len(s)), key=lambda i: (-s[i], i))[:k]


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def old_warnings(case):
    env = "old" if case["library"] == "pandas" else "mid"
    p = subprocess.run([os.path.join(ENVS, env, "bin", "python"), HARNESS],
                       input=json.dumps({"code": SETUP + case["old_code"], "mode": "values"}),
                       capture_output=True, text=True, timeout=180)
    return json.loads(p.stdout.strip().splitlines()[-1]).get("warnings", [])


def correct_chunks(case, corpus, api_key, entries):
    """(ids of the chunks of the recorded entry, ids of all chunks that describe the change)."""
    src = case["source"]
    ids = set()
    m = re.search(r"(\S+\.rst), line (\d+)", src)
    if m:
        fname, line = SOURCE_FILE[m.group(1)], int(m.group(2))
        title = open(os.path.join(NOTES, fname), encoding="utf-8").read().splitlines()[line - 1].strip()
        in_section = {c["id"] for c in corpus if c["file"] == fname and c["section"] == title}
        if in_section:  # the recorded line is the heading of a subsection: the entry is the subsection
            ids |= in_section
        else:
            ids |= {c["id"] for c in corpus if c["file"] == fname and c["line"] <= line <= c["last_line"]}
    elif "migration guide" in src:
        if "table" in src:
            name = re.split(r"[\[(]", case["old_usage"])[0].split(".")[-1].strip()
            ids |= {c["id"] for c in corpus if c["file"] == GUIDE and c["text"].split(" ")[0] == name}
        else:
            key = next((v for k, v in GUIDE_SECTION.items() if k in src), "")
            ids |= {c["id"] for c in corpus if c["file"] == GUIDE and c["section"] == key}
    recorded = set(ids)
    for e in entries:  # release-note entries that mention the same removed name or parameter
        if api_key and api_key in e["api_rows"].split() and e["category"] == "api":
            ids |= {c["id"] for c in corpus if c["entry"] == e["entry"]}
    return sorted(recorded), sorted(ids)


def main():
    corpus = []
    for lib, files in FILES.items():
        for fname in files:
            chunks = chunks_of(fname)
            for n, (line, section, text) in enumerate(chunks):
                last = chunks[n + 1][0] - 1 if n + 1 < len(chunks) else line + 1000
                corpus.append({"id": f"{fname[:-4]}:L{line}", "library": lib, "file": fname, "line": line,
                               "last_line": last, "section": section, "text": text, "entry": ""})
    # link chunks to the release-note entries of the screening (same file and first line)
    rel = {"pandas": "pandas_", "numpy": "numpy_"}
    entries = read(os.path.join(ROOT, "screening", "results", "release_note_entries.csv"))
    decisions = {d["entry"]: d["category"] for d in read(os.path.join(ROOT, "screening", "results",
                                                                      "release_note_decisions.csv"))}
    for e in entries:
        e["category"] = decisions.get(e["entry"], "")
        fname = rel[e["library"]] + e["release"].replace(" migration guide", "_migration_guide") + ".rst"
        for c in corpus:
            if c["file"] == fname and c["line"] <= int(e["line"]) <= c["last_line"]:
                c["entry"] = e["entry"]
                break

    pool = {r["id"]: r for r in read(os.path.join(ROOT, "screening", "results", "pool.csv"))}
    cases = read(os.path.join(ROOT, "test_cases", "list.csv"))
    errors = {r["id"]: r for r in read(os.path.join(HERE, "results", "error_conditions.csv"))}
    index = {lib: [c for c in corpus if c["library"] == lib] for lib in FILES}
    bm25 = {lib: BM25([c["text"] for c in index[lib]]) for lib in FILES}

    docs, runs = [], []
    for case in cases:
        cid, lib = case["id"], case["library"]
        err = errors[cid]
        prow = pool.get(case["pool_id"], {})
        m = re.match(r"removed (attribute|parameter): ([\w.]+?)(?:\((\w+)=\.\.\.\))?$", prow.get("change", ""))
        api_key = (m.group(2) + (f"({m.group(3)})" if m.group(3) else "")) if m else ""
        recorded, correct = correct_chunks(case, index[lib], api_key, entries)
        warn = old_warnings(case)
        d2 = "\n".join([c["text"] for c in index[lib] if c["id"] in recorded] + warn)
        ranked = bm25[lib].top(err["failing_line"] + "\n" + err["E2"], len(index[lib]))
        distractors = [index[lib][i]["id"] for i in ranked if index[lib][i]["id"] not in correct][:2]
        hint_names = {t for n in re.findall(r"`([^`]+)`", err["E3"][len(err["E2"]):]) for t in tokens(n)
                      if len(t) > 2 and t not in {"pd", "np", "df", "idx", "cat", "arr", "obj"}}
        names_fix = "yes" if hint_names & set(tokens(d2)) else ("no" if hint_names else "yes (by reading)")
        order = ["D2"] + distractors
        random.Random(f"{SEED}-{cid}").shuffle(order)
        docs.append({"id": cid, "library": lib, "recorded_chunks": " ".join(recorded),
                     "correct_chunks": " ".join(correct), "D2": d2,
                     "entry_names_fix": "no" if cid in ENTRY_NO_FIX else "yes", "d2_names_fix": names_fix,
                     "D3_order": " ".join(order),
                     "old_warnings": " | ".join(warn)})
        with open(os.path.join(ROOT, "test_cases", "cases", cid, "old.py"), encoding="utf-8") as f:
            program = f.read()
        for level in LEVELS:
            query = program if level == "E1" else err["failing_line"] + "\n" + err[level]
            top = [index[lib][i]["id"] for i in bm25[lib].top(query, 3)]
            runs.append({"id": cid, "level": level, "top1": top[0], "top2": top[1], "top3": top[2],
                         "recall_at_3": "yes" if set(top) & set(correct) else "no"})

    def write(name, rows, fields):
        with open(os.path.join(HERE, "results", name), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

    write("corpus.csv", corpus, ["id", "library", "file", "line", "section", "entry", "text"])
    write("documentation.csv", docs, list(docs[0]))
    write("retrieval.csv", runs, list(runs[0]))
    print(f"corpus: pandas {len(index['pandas'])} chunks, NumPy {len(index['NumPy'])} chunks")
    print(f"test cases without a correct chunk: {[d['id'] for d in docs if not d['correct_chunks']] or 'none'}")
    print(f"D2 names the fix: {sum(d['d2_names_fix'].startswith('yes') for d in docs)} of {len(docs)}; "
          f"the entry itself: {sum(d['entry_names_fix'] == 'yes' for d in docs)}")
    for level in LEVELS:
        hits = [r for r in runs if r["level"] == level and r["recall_at_3"] == "yes"]
        print(f"  recall@3 under {level}: {len(hits)} of {len(cases)}")


if __name__ == "__main__":
    main()
