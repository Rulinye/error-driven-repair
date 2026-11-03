"""Judge a model reply (Sections 3.6 and 3.9).

The first Python code block of the reply is the fix: a fenced block marked python, py or python3, or not
marked at all; blocks marked as another language (such as bash) are skipped. As in Markdown (CommonMark),
a fence may be indented by up to three spaces; some tokenizers put a space before the first fence of a
reply. That indentation is removed from the lines of the block only where all of them have it, so that
the code itself is never changed. A reply without such a block, or whose last block is not closed,
counts as a failure.

The fix is correct if its test passes in the new environment within 60 seconds and it passes the static
validity checks of test_cases/validity.py. A fix that passes the test but not the validity checks is
recorded as such, so that a more lenient success rate can also be computed (Section 4.6). A synthetic
test case (Section 3.2.5) runs with the new version of its package on the path. Library
warnings (FutureWarning, DeprecationWarning) raised while the test runs are recorded; such fixes are still
correct and are reported separately. Python's own warning about an invalid escape sequence in the fix is
not a library warning and is not recorded.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
CASES = os.path.join(ROOT, "test_cases", "cases")
SYNTHETIC = os.path.join(ROOT, "synthetic")
SYNTHETIC_NEW = {"fernledger": "2.0.0", "gridwell": "1.0.0", "quillery": "4.0.0"}
sys.path.insert(0, os.path.join(ROOT, "test_cases"))
from validity import check  # noqa: E402

TIMEOUT = 60
FENCE = re.compile(r"^( {0,3})```[ \t]*([\w+-]*)[^\n]*\n(.*?)^ {0,3}```[ \t]*$", re.S | re.M)
PYTHON = {"", "python", "py", "python3"}
HEADER = re.compile(r"^[A-Za-z_][\w.]*(Error|Exception|Interrupt|Exit)\b")
WARNING = re.compile(r"\b(FutureWarning|DeprecationWarning|PendingDeprecationWarning)\b")
NEW_ENV = {"pandas": "mid", "NumPy": "new"}


def extract(reply):
    """The code of the first Python code block in the reply, or None."""
    for m in FENCE.finditer(reply):
        if m.group(2).lower() in PYTHON:
            code = m.group(3)
            lines = [line for line in code.splitlines() if line.strip()]
            common = min((len(line) - len(line.lstrip(" ")) for line in lines), default=0)
            indent = min(len(m.group(1)), common)
            return re.sub(rf"^ {{{indent}}}", "", code, flags=re.M) if indent else code
    return None


def case_dir(cid):
    """The folder of a test case: a synthetic one (S01), a second one (P01b) or one of the 90."""
    if cid.startswith("S") and os.path.isdir(os.path.join(SYNTHETIC, "cases", cid)):
        return os.path.join(SYNTHETIC, "cases", cid)
    if cid.endswith("b"):
        return os.path.join(ROOT, "test_cases", "second", cid)
    return os.path.join(CASES, cid)


def run_test(python, cid, code, path=None):
    """Run the test of a case on the code, with path on PYTHONPATH if given; return (passed, error,
    warnings)."""
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "solution.py"), "w", encoding="utf-8") as f:
            f.write(code)
        shutil.copy(os.path.join(case_dir(cid), "test.py"), os.path.join(tmp, "test.py"))
        env = dict(os.environ, PYTHONPATH=path) if path else None
        try:
            p = subprocess.run([python, "-W", "default", "test.py"], cwd=tmp, capture_output=True, text=True,
                               timeout=TIMEOUT, check=False, env=env)
        except subprocess.TimeoutExpired:
            return False, "timeout", ""
    passed = p.returncode == 0 and p.stdout.strip().endswith("PASS")
    lines = p.stderr.rstrip().splitlines()
    starts = [i for i, line in enumerate(lines) if HEADER.match(line)]
    error = "" if passed else ("\n".join(lines[starts[-1]:]) if starts else "\n".join(lines[-1:]))
    warnings = sorted({m.group(1) for line in lines
                       if (m := WARNING.search(line)) and "invalid escape sequence" not in line})
    return passed, error, " ".join(warnings)


def judge(envs, cid, library, reply, old_code):
    """Outcome of one reply: a dict with the code, whether it is correct, and why not."""
    code = extract(reply or "")
    if code is None:
        return {"outcome": "no code block", "correct": False, "passes_test": False, "violations": "",
                "error": "", "warnings": "", "code": ""}
    path = None
    if library in SYNTHETIC_NEW:
        python = os.path.join(os.path.abspath(envs), "new", "bin", "python")
        path = os.path.join(SYNTHETIC, "packages", library, SYNTHETIC_NEW[library])
    else:
        python = os.path.join(os.path.abspath(envs), NEW_ENV[library], "bin", "python")
    passed, error, warnings = run_test(python, cid, code, path)
    violations = check(code, old_code)
    if passed and not violations:
        outcome = "correct"
    elif passed:
        outcome = "fails the validity checks"
    else:
        outcome = "fails the test"
    return {"outcome": outcome, "correct": outcome == "correct", "passes_test": passed,
            "violations": "; ".join(violations), "error": error[-500:], "warnings": warnings, "code": code}
