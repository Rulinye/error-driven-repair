"""Build the five error-message conditions E0-E4 for every test case (Section 3.4).

usage: python conditions/error_variants.py
Reads test_cases/list.csv; uses the environments of measurements/ and the harness
measurements/scripts/harness.py. Writes conditions/results/error_conditions.csv.

  E0  the exception type and message as printed by Python 3.11, including any "Did you mean" suggestion
  E1  only the statement that the code fails after the upgrade
  E2  E0 without the interpreter's suggestion, URLs, and sentences that contain a suggestion phrase
      ("use", "instead", "might want to try") or name an API other than the failing one
  E3  E2 plus the correct hint: "Use X instead." or "Remove the argument X."; for behavior changes, a
      sentence that describes the change and the fix
  E4  E2 plus a misleading hint in the interpreter's style, "Did you mean: 'Y'?", where Y is the public
      attribute or parameter of the same object, module or function whose name is closest to the removed
      one under the interpreter's distance measure (CPython 3.11, Python/suggestions.c), without its
      cutoff, excluding the correct fix (the names of the recorded replacement); for behavior changes, a
      plausible but wrong description
The misleading hint is checked: the old code with Y in place of the removed name must fail in the new
version or give a different result (value, type or dtype) from the old code in the old version.
Otherwise the next closest name is used. The check and the failing line use the minimal call of each
change; both are repeated on the drafted test cases, whose tests decide what counts as a correct fix.
"""
import csv
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
ENVS = os.path.join(ROOT, "measurements", "envs")
HARNESS = os.path.join(ROOT, "measurements", "scripts", "harness.py")
SETUP = "import io, datetime, functools, numpy as np, pandas as pd\n"
VERSIONS = {"pandas": ("1.5.3", "2.2.3"), "NumPy": ("1.23.5", "2.1.3")}
HINT = re.compile(r"\b(use|instead)\b|might want to try", re.I)
PATH_RE = re.compile(r"\(?/[^\s()'\"]*site-packages/[^\s()'\"]*\)?")

# Callable whose parameters are the candidates for E4, for removed parameters
PARAM_TARGET = {
    "P20": "pd.DataFrame.info", "P21": "pd.DataFrame.groupby", "P22": "pd.DataFrame.to_csv",
    "P23": "pd.DataFrame.set_axis", "P24": "pd.Index.copy", "P25": "pd.DatetimeIndex.to_series",
    "P30": "pd.Series.sum", "P31": "pd.read_csv", "P32": "pd.read_csv", "P33": "pd.read_csv",
    "P34": "pd.Series.resample", "P35": "pd.Series.resample", "P36": "pd.Series.between_time",
    "P37": "pd.date_range", "P38": "pd.Categorical.set_categories", "P39": "pd.factorize",
    "P40": "pd.Series.where", "P41": "pd.DataFrame.describe", "P42": "pd.Series.expanding",
    "P43": "pd.Index.get_loc", "P63": "pd.DataFrame.any", "P64": "pd.PeriodIndex.get_loc",
    "P65": "pd.Series.sem", "P66": "pd.lreshape", "N34": "np.histogram", "N41": "np.histogram2d",
}
# Object whose public attributes are the candidates for E4, where the exception does not carry it
ATTR_TARGET = {"module 'pandas'": "pd", "np.": "np", "module 'numpy'": "np", "ndarray class": "np.arange(3)"}

# Hints for the behavior changes, written by hand; E4_FIX is the code that follows the misleading hint
BEHAVIOR = {
    "P45": ("In pandas 2.0, numeric_only defaults to False, so non-numeric columns raise an error; "
            "pass numeric_only=True.",
            "In pandas 2.0, groupby keeps the group keys unsorted, so mixed-type columns raise an error; "
            "pass sort=False.",
            "df = pd.DataFrame({'k': [1, 1], 'v': [1, 2], 't': ['x', 'y']})\nresult = df.groupby('k', sort=False).mean()"),
    "P47": ("In pandas 2.0, to_datetime infers one format from the first element and applies it to all; "
            "pass format='mixed' and, for day-first dates, dayfirst=True.",
            "In pandas 2.0, to_datetime converts strings to UTC by default; pass utc=False.",
            "result = pd.to_datetime(['13-01-2000', '2000-01-12'], utc=False)"),
    "P49": ("In pandas 2.0, only the resolutions 's', 'ms', 'us' and 'ns' are supported; pass dtype='datetime64[s]'.",
            "In pandas 2.0, datetime64 dtypes need an explicit time zone; pass dtype='datetime64[D, UTC]'.",
            "result = pd.Series(['2020-01-01'], dtype='datetime64[D, UTC]')"),
    "P50": ("In pandas 2.0, only the resolutions 's', 'ms', 'us' and 'ns' are supported; use astype('datetime64[s]').",
            "In pandas 2.0, astype to datetime64 no longer copies implicitly; pass copy=True.",
            "result = pd.Series(pd.to_datetime(['2020-01-01 10:00'])).astype('datetime64[D]', copy=True)"),
    "P53": ("In pandas 2.0, floats that are not whole numbers are no longer cast silently to an integer dtype; "
            "create the Series without the integer dtype.",
            "In pandas 2.0, integer dtypes must be given as NumPy types; pass dtype=np.int64.",
            "result = pd.Series([1.5, 2.0], dtype=np.int64)"),
    "N36": ("In NumPy 2.0, a Python integer takes the dtype of the NumPy operand (NEP 50), so 300 does not fit "
            "uint8; convert to a Python int or a wider dtype first.",
            "In NumPy 2.0, scalar arithmetic needs an explicit array; pass the operand through np.asarray first.",
            "result = int(np.asarray(np.uint8(1)) + 300)"),
    "P67": ("In pandas 2.0, the arguments of DataFrame.set_index other than keys are keyword-only; "
            "pass drop by keyword.",
            "In pandas 2.0, DataFrame.set_index takes the keys as a list; pass the keys as a list.",
            "df = pd.DataFrame({'a': [1, 2, 3], 'b': [4.0, 5.0, 6.0]})\nresult = df.set_index(['a'], False)"),
    "P68": ("In pandas 2.0, Categorical no longer accepts a scalar as data; pass a list such as ['a'].",
            "In pandas 2.0, Categorical needs its categories; pass categories=['a'].",
            "result = list(pd.Categorical('a', categories=['a']))"),
    "P69": ("In pandas 2.0, inclusive must be one of 'both', 'neither', 'left' or 'right'; pass inclusive='both'.",
            "In pandas 2.0, inclusive must be one of 'both', 'neither', 'left' or 'right'; pass inclusive='left'.",
            "s = pd.Series([1.0, 2.0, 3.0])\nresult = s.between(1.0, 2.0, inclusive='left')"),
}
# Sentences dropped from E2 by hand: NumPy's alias messages name the builtin that replaces the alias
# (the fix) with the same spelling as the failing name, and then refer back to the removed suggestion
E2_DROP_BY_HAND = [r"was a deprecated alias for the builtin", r"^Doing this will not modify any behavior and is safe\.$"]
# Correct hint where the recorded replacement does not read as a single fix
E3_OVERRIDE = {
    "N01": "Use `float` instead.", "N02": "Use `int` instead.",
    "N22": "Use `np.result_type` or `np.promote_types` instead.",
    "P35": "Shift the index after resampling instead: `res.index = res.index + pd.Timedelta(loffset)`.",
    "P41": "Remove the argument `datetime_is_numeric`.",
}
# The correct fix, which E4 must not name
FIX_NAME = {
    "P20": "show_counts", "P22": "lineterminator", "P32": "on_bad_lines", "P34": "offset", "P35": "offset",
    "P36": "inclusive", "P37": "inclusive", "P39": "use_na_sentinel", "N34": "density", "N41": "density",
}


def python(env):
    return os.path.join(ENVS, env, "bin", "python")


def envs_of(library):
    return ("old", "mid") if library == "pandas" else ("mid", "new")


PROBE = r'''
import json, sys, traceback, inspect, io, datetime, functools
import numpy as np, pandas as pd
spec = json.load(sys.stdin)
ns = {"np": np, "pd": pd, "io": io, "datetime": datetime, "functools": functools}
out = {"line": "", "obj_dir": None, "params": None}
try:
    exec(compile(spec["code"], "<case>", "exec"), ns)
except BaseException as e:
    frames = [f for f in traceback.extract_tb(e.__traceback__) if f.filename == "<case>"]
    if frames:
        out["line"] = spec["code"].splitlines()[frames[-1].lineno - 1].strip()
    obj = getattr(e, "obj", None) if isinstance(e, AttributeError) else None
    if obj is not None:
        out["obj_dir"] = sorted(dir(obj))
if spec.get("attr_target"):
    out["obj_dir"] = sorted(dir(eval(spec["attr_target"], ns)))
if spec.get("param_target"):
    sig = inspect.signature(eval(spec["param_target"], ns))
    out["params"] = [p.name for p in sig.parameters.values() if p.name != "self" and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)]
print(json.dumps(out))
'''


def printed_error(env, code):
    """The exception text the interpreter prints for the uncaught error (no stack frames)."""
    p = subprocess.run([python(env), "-W", "ignore", "-c", SETUP + code], capture_output=True, text=True, timeout=180)
    if "Traceback (most recent call last):" not in p.stderr:
        return ""
    block = p.stderr.rsplit("Traceback (most recent call last):", 1)[1].splitlines()[1:]
    i = 0
    while i < len(block) and (block[i].startswith("  ") or not block[i].strip()):
        i += 1
    return PATH_RE.sub("<site-packages path>", "\n".join(block[i:]).strip())


def probe(env, code, attr_target=None, param_target=None):
    p = subprocess.run([python(env), "-W", "ignore", "-c", PROBE], capture_output=True, text=True, timeout=180,
                       input=json.dumps({"code": code, "attr_target": attr_target, "param_target": param_target}))
    return json.loads(p.stdout.strip().splitlines()[-1])


def harness(env, code, mode):
    p = subprocess.run([python(env), HARNESS], input=json.dumps({"code": SETUP + code, "mode": mode}),
                       capture_output=True, text=True, timeout=180)
    return json.loads(p.stdout.strip().splitlines()[-1])


# ---- the interpreter's distance measure (CPython 3.11, Python/suggestions.c), without the cutoff ----
MOVE_COST, CASE_COST = 2, 1


def substitution_cost(a, b):
    if (ord(a) & 31) != (ord(b) & 31):
        return MOVE_COST
    if a == b:
        return 0
    return CASE_COST if a.lower() == b.lower() else MOVE_COST


def levenshtein(a, b):
    while a and b and a[0] == b[0]:
        a, b = a[1:], b[1:]
    while a and b and a[-1] == b[-1]:
        a, b = a[:-1], b[:-1]
    if not a or not b:
        return (len(a) + len(b)) * MOVE_COST
    if len(b) < len(a):
        a, b = b, a
    row = [(i + 1) * MOVE_COST for i in range(len(a))]
    result = 0
    for bi, code in enumerate(b):
        distance = result = bi * MOVE_COST
        for i, ch in enumerate(a):
            substitute = distance + substitution_cost(code, ch)
            distance = row[i]
            result = min(min(result, distance) + MOVE_COST, substitute)
            row[i] = result
    return result


def ranked(name, candidates, exclude):
    """Public candidates ordered by distance to name; ties keep the order of dir() (alphabetical)."""
    pool = [c for c in candidates if not c.startswith("_") and c != name and c not in exclude]
    return sorted(pool, key=lambda c: levenshtein(name, c))


# ---- E2 and E3 ----
def strip_hint(e0, failing_name):
    """E2: drop the interpreter's suggestion, URLs, and sentences with a suggestion phrase or another API."""
    text = re.sub(r"\.? Did you mean:? '?[^'?]+'?\?\s*$", "", e0.strip())
    head, _, msg = text.partition(": ")
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z`'])", msg)
    kept, dropped = [], []
    allowed = {failing_name, f"np.{failing_name}", f"numpy.{failing_name}"}
    for s in sentences:
        others = [n for n in re.findall(r"`([^`]+)`", s) if n not in allowed]
        by_hand = any(re.search(p, s.strip()) for p in E2_DROP_BY_HAND)
        if HINT.search(s) or re.search(r"https?://", s) or others or by_hand:
            dropped.append(s)
        else:
            kept.append(s)
    e2 = head + ": " + " ".join(kept) if kept else head
    return e2.rstrip(), dropped


def correct_hint(case):
    cid = case["id"]
    if cid in BEHAVIOR:
        return BEHAVIOR[cid][0]
    if cid in E3_OVERRIDE:
        return E3_OVERRIDE[cid]
    repl = case["replacement"].strip()
    m = re.match(r"remove the (\w+) argument", repl, re.I)
    if m:
        return f"Remove the argument `{m.group(1)}`."
    return f"Use `{repl}` instead."


def with_sentence(e2, sentence):
    return e2 + (" " if e2.endswith((".", "!", "?")) else ". ") + sentence


def failing_name(e0):
    for pattern in (r"has no attribute '(\w+)'", r"unexpected keyword argument '(\w+)'", r"`np\.(\w+)` was removed",
                    r"`(\w+)` was removed from the ndarray class", r"cannot import name '(\w+)'"):
        m = re.search(pattern, e0)
        if m:
            return m.group(1)
    return ""


def fix_names(case):
    """Names that belong to the correct fix: the identifiers of the recorded replacement that are not
    already in the old usage (variables such as key or idx appear in both)."""
    ident = r"[A-Za-z_]\w*"
    names = set(re.findall(ident, case["replacement"])) - set(re.findall(ident, case["old_usage"]))
    if case["id"] in FIX_NAME:
        names.add(FIX_NAME[case["id"]])
    return names


def typed(code):
    """The code with the type and dtype of its result added, so that a check also compares them."""
    return code + "\nresult = (result, type(result).__name__, str(getattr(result, 'dtype', '')))"


def outcome(run, old):
    if run["status"] != "ok":
        return "fails"
    same = json.dumps(run["result"], sort_keys=True) == json.dumps(old["result"], sort_keys=True)
    return "same result" if same else "different result"


def substitute(code, name, new, is_param):
    if is_param:
        return re.sub(rf"\b{re.escape(name)}=", f"{new}=", code)
    return re.sub(rf"(?<=\.){re.escape(name)}\b", new, code)


def main():
    with open(os.path.join(ROOT, "test_cases", "list.csv"), newline="", encoding="utf-8") as f:
        cases = list(csv.DictReader(f))
    rows = []
    for case in cases:
        cid, lib = case["id"], case["library"]
        old_env, new_env = envs_of(lib)
        code = case["old_code"]
        e0 = printed_error(new_env, code)
        name = failing_name(e0)
        e1 = f"The code fails after upgrading {lib} from {VERSIONS[lib][0]} to {VERSIONS[lib][1]}."
        e2, dropped = strip_hint(e0, name)
        e3 = with_sentence(e2, correct_hint(case))
        is_param = cid in PARAM_TARGET
        attr_target = next((v for k, v in ATTR_TARGET.items() if k in e0), None) if not is_param else None
        info = probe(new_env, code, attr_target=attr_target, param_target=PARAM_TARGET.get(cid))
        old = harness(old_env, typed(code), case["mode"])
        e4_name, e4_check, e4 = "", "", ""
        if cid in BEHAVIOR:
            e4 = with_sentence(e2, BEHAVIOR[cid][1])
            r = harness(new_env, typed(BEHAVIOR[cid][2]), case["mode"])
            e4_check = outcome(r, old)
        else:
            candidates = info["params"] if is_param else (info["obj_dir"] or [])
            for cand in ranked(name, candidates, fix_names(case)):
                r = harness(new_env, typed(substitute(code, name, cand, is_param)), case["mode"])
                if outcome(r, old) != "same result":
                    e4_name = cand
                    e4_check = outcome(r, old)
                    break
            e4 = with_sentence(e2, f"Did you mean: '{e4_name}'?") if e4_name else ""
        rows.append({"id": cid, "library": lib, "failing_line": info["line"], "removed_name": name,
                     "E0": e0, "E1": e1, "E2": e2, "E3": e3, "E4": e4, "e4_name": e4_name, "e4_check": e4_check,
                     "e2_dropped": " | ".join(dropped), "e0_equals_e2": "yes" if e0 == e2 else ""})
        print(f"{cid}  E4: {e4_name or '(by hand)':24s} {e4_check}")

    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    path = os.path.join(HERE, "results", "error_conditions.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} test cases -> {path}; E0 equals E2 for {sum(1 for r in rows if r['e0_equals_e2'])}")


if __name__ == "__main__":
    main()
