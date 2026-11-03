"""Prompts for the main runs (Section 3.6).

Every condition uses one template. It states the library and both versions, shows the old program, then
the error text of the condition (if any) and its documentation (if any), and asks for the complete fixed
program in one Python code block. The paraphrased template says the same in other words and another
order; it is used for the sensitivity check on the six conditions of the primary contrasts (Section 4.4).

The error texts come from conditions/results/error_conditions.csv. Under E1 there is no error, so the
statement that the code fails after the upgrade takes its place. The documentation comes from
conditions/results/documentation.csv (D2, D3) and retrieval.csv (D1); D0 has none. D1, D2 and D3 have the
same heading, so the prompt does not tell the model which level it sees.

The 15 synthetic test cases (Section 3.2.5) are read from synthetic/results/ and synthetic/cases/, and the 30
second test cases of the replication subset (Section 3.2.3, ids such as P01b) from test_cases/second/, when they
have been built (synthetic/build.py, test_cases/build_second.py); they are kept in `synthetic` and `second`,
apart from the 90 test cases in `cases`.
"""
import csv
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
RESULTS = os.path.join(ROOT, "conditions", "results")
CASES = os.path.join(ROOT, "test_cases", "cases")
SYNTHETIC = os.path.join(ROOT, "synthetic")
SECOND = os.path.join(ROOT, "test_cases", "second")

VERSIONS = {"pandas": ("pandas", "1.5.3", "2.2.3"), "NumPy": ("NumPy", "1.23.5", "2.1.3"),
            "fernledger": ("fernledger", "1.6.0", "2.0.0"), "gridwell": ("gridwell", "0.9.4", "1.0.0"),
            "quillery": ("quillery", "3.2.1", "4.0.0")}
LEVELS_E = ["E0", "E1", "E2", "E3", "E4"]
LEVELS_D = ["D0", "D1", "D2", "D3"]
ALL = [e + d for e in LEVELS_E for d in LEVELS_D]
# The six conditions of the primary contrasts, and E0 without documentation for RQ1 (Section 4.2)
PRIMARY = ["E2D0", "E3D0", "E4D0", "E2D2", "E3D2", "E4D2", "E0D0"]
REST = [c for c in ALL if c not in PRIMARY]
PARAPHRASE = PRIMARY[:6]

MAIN = """This code was written for {lib} {old} and is now run with {lib} {new}.

```python
{program}
```

{sections}Fix the code so that it works with {lib} {new}. Return only the complete fixed code in one Python code block."""

PARAPHRASED = """After upgrading {lib} from {old} to {new}, the code below no longer works.

{sections}```python
{program}
```

Rewrite the code so that it runs with {lib} {new}. Give only the full code in one Python code block."""

TEMPLATES = {"main": MAIN, "paraphrase": PARAPHRASED}


def _read(name, folder=RESULTS):
    with open(os.path.join(folder, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class Conditions:
    """The error texts and documentation of every test case."""

    def __init__(self):
        self.errors = {r["id"]: r for r in _read("error_conditions.csv")}
        self.docs = {r["id"]: r for r in _read("documentation.csv")}
        self.retrieved = {(r["id"], r["level"]): r for r in _read("retrieval.csv")}
        self.chunks = {r["id"]: r["text"] for r in _read("corpus.csv")}
        self.cases = sorted(self.errors, key=lambda c: (c[0] == "N", c))
        self.synthetic = []
        synthetic = os.path.join(SYNTHETIC, "results")
        if os.path.exists(os.path.join(synthetic, "error_conditions.csv")):
            errors = {r["id"]: r for r in _read("error_conditions.csv", synthetic)}
            self.errors.update(errors)
            self.docs.update({r["id"]: r for r in _read("documentation.csv", synthetic)})
            self.retrieved.update({(r["id"], r["level"]): r for r in _read("retrieval.csv", synthetic)})
            self.chunks.update({r["id"]: r["text"] for r in _read("corpus.csv", synthetic)})
            self.synthetic = sorted(errors)
        self.second = []
        second = os.path.join(SECOND, "results")
        if os.path.exists(os.path.join(second, "error_conditions.csv")):
            errors = {r["id"]: r for r in _read("error_conditions.csv", second)}
            self.errors.update(errors)
            self.docs.update({r["id"]: r for r in _read("documentation.csv", second)})
            self.retrieved.update({(r["id"], r["level"]): r for r in _read("retrieval.csv", second)})
            self.second = sorted(errors, key=lambda c: (c[0] == "N", c))

    def program(self, cid):
        folder = os.path.join(SYNTHETIC, "cases") if cid in self.synthetic else SECOND if cid in self.second else CASES
        with open(os.path.join(folder, cid, "old.py"), encoding="utf-8") as f:
            return f.read().rstrip("\n")

    def error_section(self, cid, level):
        text = self.errors[cid][level]
        if level == "E1":
            return text
        return f"Error:\n```\n{text}\n```"

    def documentation(self, cid, e, d):
        if d == "D0":
            return ""
        if d == "D1":
            r = self.retrieved[(cid, e)]
            parts = [self.chunks[r[k]] for k in ("top1", "top2", "top3")]
        elif d == "D2":
            parts = [self.docs[cid]["D2"]]
        else:
            parts = [self.docs[cid]["D2"] if x == "D2" else self.chunks[x]
                     for x in self.docs[cid]["D3_order"].split()]
        return "\n\n".join(parts)

    def prompt(self, cid, condition, template="main"):
        e, d = condition[:2], condition[2:]
        lib, old, new = VERSIONS[self.errors[cid]["library"]]
        sections = self.error_section(cid, e) + "\n\n"
        docs = self.documentation(cid, e, d)
        if docs:
            sections += f"Documentation:\n{docs}\n\n"
        return TEMPLATES[template].format(lib=lib, old=old, new=new, program=self.program(cid),
                                          sections=sections)


def prompt_id(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def plan(conds, cases, conditions, template="main"):
    """The distinct prompts for the given cases and conditions.

    Returns {prompt id: {"case": id, "text": prompt, "conditions": [conditions that share it]}}.
    Conditions of one case whose prompts are identical share one prompt and its samples (Section 4.2).
    """
    out = {}
    for cid in cases:
        for c in conditions:
            text = conds.prompt(cid, c, template)
            pid = prompt_id(text)
            entry = out.setdefault(pid, {"case": cid, "text": text, "conditions": []})
            assert entry["case"] == cid, (cid, c)
            entry["conditions"].append(c)
    return out
