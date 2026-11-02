"""Knowledge probe (Section 3.8): one question per test case, and the fix an answer must give.

usage: python probe/questions.py
Reads test_cases/list.csv; writes probe/results/questions.csv.

The question depends on the type of change:
  removed API        "In <library> <new version>, <old API> was removed. What should be used instead?"
  removed parameter  "In <library> <new version>, the parameter <parameter> of <function> was removed.
                      How should a call that uses it be changed?"
  behavior change    "In <library> <new version>, the behavior of <call> changed. What argument or
                      conversion keeps the old result?"

An answer is correct if it gives the recorded fix. FIX lists, for each test case, the ways of giving
it: each alternative is a list of patterns that must all occur in the answer. A plain pattern is an
identifier, matched as a whole word; a pattern that starts with "re:" is a regular expression.
REVIEW lists the test cases whose fix cannot be matched on identifiers (removing an argument,
assigning the result, a conversion); every answer to them is checked by hand. NEAR lists names that
come close to the fix without being the recorded one; an answer that contains one is also checked by
hand.
"""
import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
NEW_VERSION = {"pandas": "pandas 2.2.3", "numpy": "NumPy 2.1.3"}

REMOVE = (r"re:(?i)\b(remove|removing|drop|dropping|omit|omitting|delete|leave (it )?out|no longer (needed|necessary)"
          r"|(do not|don't) pass|without (passing|the))\b")

# id: ("api", old API, fix) | ("param", parameter, function, fix) | ("behavior", call, fix)
SPEC = {
    "P01": ("api", "DataFrame.append", [["concat"]]),
    "P02": ("api", "Series.append", [["concat"]]),
    "P03": ("api", "DataFrame.iteritems", [["items"]]),
    "P04": ("api", "Series.iteritems", [["items"]]),
    "P05": ("api", "pandas.Int64Index", [["Index"]]),
    "P06": ("api", "pandas.Float64Index", [["Index"]]),
    "P07": ("api", "pandas.UInt64Index", [["Index"]]),
    "P09": ("api", "Index.is_monotonic", [["is_monotonic_increasing"]]),
    "P10": ("api", "Series.is_monotonic", [["is_monotonic_increasing"]]),
    "P11": ("api", "DatetimeIndex.week", [["isocalendar"]]),
    "P12": ("api", "Series.dt.week", [["isocalendar"]]),
    "P13": ("api", "Categorical.to_dense", [["asarray"], [r"re:\b(np|numpy)\.array\("]]),
    "P14": ("api", "Categorical.mode", [["Series", "mode"]]),
    "P15": ("api", "Index.to_native_types", [[r"re:astype\(\s*str\b"]]),
    "P16": ("api", "Index.is_mixed", [["inferred_type"]]),
    "P18": ("api", "DatetimeIndex.to_perioddelta", [["to_period", "to_timestamp"]]),
    "P20": ("param", "null_counts", "DataFrame.info", [["show_counts"]]),
    "P21": ("param", "squeeze", "DataFrame.groupby", [[REMOVE]]),
    "P22": ("param", "line_terminator", "DataFrame.to_csv", [["lineterminator"]]),
    "P23": ("param", "inplace", "DataFrame.set_axis",
            [[r"re:=\s*[\w.]+\.set_axis\("], [r"re:\bassign"], [r"re:returns? (a )?new"]]),
    "P24": ("param", "dtype", "Index.copy", [["astype"]]),
    "P25": ("param", "keep_tz", "DatetimeIndex.to_series", [[REMOVE]]),
    "P26": ("api", "Series.mad", [[r"re:\.abs\(\)", r"re:\.mean\(\)"]]),
    "P27": ("api", "DataFrame.mad", [[r"re:\.abs\(\)", r"re:\.mean\(\)"]]),
    "P28": ("api", "Series.tshift", [["shift", "freq"]]),
    "P30": ("param", "level", "Series.sum", [[r"re:groupby\([^)]*level"]]),
    "P31": ("param", "squeeze", "pandas.read_csv", [[r"re:\.squeeze\("]]),
    "P32": ("param", "error_bad_lines", "pandas.read_csv", [["on_bad_lines"]]),
    "P33": ("param", "prefix", "pandas.read_csv", [["add_prefix"]]),
    "P34": ("param", "base", "Series.resample", [["offset"]]),
    "P35": ("param", "loffset", "Series.resample",
            [[r"re:index\s*(\+|=)"], [r"re:\.shift\("], ["Timedelta"], ["to_offset"]]),
    "P36": ("param", "include_end", "Series.between_time", [["inclusive"]]),
    "P37": ("param", "closed", "pandas.date_range", [["inclusive"]]),
    "P38": ("param", "inplace", "Categorical.set_categories",
            [[r"re:=\s*[\w.]+\.set_categories\("], [r"re:\bassign"], [r"re:returns? (a )?new"]]),
    "P39": ("param", "na_sentinel", "pandas.factorize", [["use_na_sentinel"]]),
    "P40": ("param", "errors", "Series.where", [[REMOVE]]),
    "P41": ("param", "datetime_is_numeric", "DataFrame.describe", [[REMOVE]]),
    "P42": ("param", "center", "Series.expanding", [[REMOVE]]),
    "P43": ("param", "method", "Index.get_loc", [["get_indexer"]]),
    "P44": ("api", "DataFrameGroupBy.pad", [["ffill"]]),
    "P45": ("behavior", "df.groupby(key).mean() on a DataFrame that has text columns",
            [[r"re:numeric_only\s*=\s*True"]]),
    "P47": ("behavior", "pandas.to_datetime() on a list of date strings that are not all written in the same format",
            [[r"re:['\"`]mixed['\"`]"], [r"re:format\s*=\s*\S?mixed"]]),
    "P49": ("behavior", "pandas.Series(data, dtype='datetime64[D]')",
            [[r"re:datetime64\[(s|ms|us|ns)\]"], [r"re:M8\[(s|ms|us|ns)\]"]]),
    "P50": ("behavior", "Series.astype('datetime64[D]')",
            [[r"re:datetime64\[(s|ms|us|ns)\]"], [r"re:M8\[(s|ms|us|ns)\]"]]),
    "P53": ("behavior", "pandas.Series([1.5, 2.0], dtype='int64')",
            [[r"re:\bfloat"], [r"re:\b(remove|drop|omit|without|no)\b[^.]*\bdtype"]]),
    "P54": ("api", "DatetimeIndex.union_many", [["union"]]),
    "P61": ("api", "Categorical.take_nd", [["take"]]),
    "P62": ("api", "DatetimeArray.weekofyear", [["isocalendar"]]),
    "P63": ("param", "level", "DataFrame.any", [[r"re:groupby\([^)]*level"]]),
    "P64": ("param", "method", "PeriodIndex.get_loc", [["get_indexer"]]),
    "P65": ("param", "level", "Series.sem", [[r"re:groupby\([^)]*level"]]),
    "P66": ("param", "label", "pandas.lreshape", [[REMOVE]]),
    "P67": ("behavior", "DataFrame.set_index(keys, False)", [[r"re:drop\s*=\s*False"], [r"re:\bkeyword"]]),
    "P68": ("behavior", "pandas.Categorical('a')", [[r"re:Categorical\(\s*\["], [r"re:\blist\b"]]),
    "P69": ("behavior", "Series.between(left, right, inclusive=True)", [[r"re:['\"`]both['\"`]"]]),
    "N01": ("api", "numpy.float", [[r"re:(?<![\w.])float\b(?![\d_])"], ["float64"]]),
    "N02": ("api", "numpy.int", [[r"re:(?<![\w.])int\b(?![\d_])"], ["int64"]]),
    "N04": ("api", "numpy.object", [[r"re:(?<![\w.])object\b(?!_)"]]),
    "N05": ("api", "numpy.str", [[r"re:(?<![\w.])str\b(?!_)"]]),
    "N06": ("api", "numpy.float_", [["float64"]]),
    "N07": ("api", "numpy.complex_", [["complex128"]]),
    "N08": ("api", "numpy.string_", [["bytes_"]]),
    "N09": ("api", "numpy.unicode_", [["str_"]]),
    "N10": ("api", "numpy.NaN", [["nan"]]),
    "N11": ("api", "numpy.Inf", [["inf"]]),
    "N12": ("api", "numpy.infty", [["inf"]]),
    "N13": ("api", "numpy.NINF", [[r"re:-\s*((np|numpy)\.)?inf\b"]]),
    "N14": ("api", "numpy.product", [["prod"]]),
    "N15": ("api", "numpy.cumproduct", [["cumprod"]]),
    "N16": ("api", "numpy.alltrue", [[r"re:\b(np|numpy)\.all\b"], [r"re:\.all\(\)"]]),
    "N17": ("api", "numpy.sometrue", [[r"re:\b(np|numpy)\.any\b"], [r"re:\.any\(\)"]]),
    "N18": ("api", "numpy.round_", [[r"re:\b(np|numpy)\.round\b(?!_)"]]),
    "N19": ("api", "numpy.asfarray", [["asarray", r"re:\bfloat"]]),
    "N20": ("api", "numpy.cast", [["asarray"]]),
    "N21": ("api", "numpy.mat", [["asmatrix"]]),
    "N22": ("api", "numpy.find_common_type", [["result_type"], ["promote_types"]]),
    "N23": ("api", "numpy.issubsctype", [["issubdtype"]]),
    "N24": ("api", "numpy.issubclass_", [[r"re:(?<![\w.])issubclass\b(?!_)"]]),
    "N26": ("api", "numpy.longfloat", [["longdouble"]]),
    "N27": ("api", "numpy.cfloat", [["complex128"]]),
    "N28": ("api", "numpy.obj2sctype", [["dtype", r"re:\.type\b"]]),
    "N29": ("api", "numpy.sctype2char", [["dtype", r"re:\.char\b"]]),
    "N30": ("api", "numpy.nbytes", [["itemsize"]]),
    "N32": ("api", "ndarray.ptp", [[r"re:\b(np|numpy)\.ptp\b"]]),
    "N33": ("api", "ndarray.newbyteorder", [["view", r"re:dtype\.newbyteorder"]]),
    "N34": ("param", "normed", "numpy.histogram", [["density"]]),
    "N36": ("behavior", "numpy.uint8(1) + 300",
            [[r"re:(?<![\w.])int\("], [r"re:\.item\(\)"], [r"re:\b(u?int(16|32|64)|int_)\b"], ["astype"],
             [r"re:\bPython int"], [r"re:\bwider\b"]]),
    "N37": ("api", "numpy.AxisError", [[r"re:\bexceptions\.AxisError\b"], [r"re:\bexceptions import\b[\w, ]*\bAxisError\b"]]),
    "N38": ("api", "numpy.VisibleDeprecationWarning", [[r"re:\bexceptions\.VisibleDeprecationWarning\b"],
                                                       [r"re:\bexceptions import\b[\w, ]*\bVisibleDeprecationWarning\b"]]),
    "N41": ("param", "normed", "numpy.histogram2d", [["density"]]),
}
REVIEW = {"P21", "P23", "P25", "P35", "P38", "P40", "P41", "P42", "P53", "P66", "P68", "N36"}
NEAR = {
    "P13": ["to_numpy"], "P15": ["astype"], "P16": ["infer_dtype"], "P33": ["names"], "P34": ["origin"],
    "P45": ["select_dtypes"], "P47": ["dayfirst", "ISO8601", "infer_datetime_format"],
    "N02": ["int_"], "N04": ["object_"], "N05": ["str_"], "N18": ["around"], "N19": ["array"],
    "N20": ["astype"],
}


def pattern(p):
    if p.startswith("re:"):
        return re.compile(p[3:])
    return re.compile(r"(?<!\w)" + re.escape(p) + r"(?!\w)")


def matches(cid, answer):
    """True if the answer gives the recorded fix of the test case."""
    return any(all(pattern(p).search(answer) for p in alt) for alt in SPEC[cid][-1])


def near(cid, answer):
    return any(pattern(p).search(answer) for p in NEAR.get(cid, []))


def question(cid, library):
    kind, *fields = SPEC[cid]
    lib = NEW_VERSION[library]
    if kind == "api":
        return f"In {lib}, {fields[0]} was removed. What should be used instead?"
    if kind == "param":
        return (f"In {lib}, the parameter {fields[0]} of {fields[1]} was removed. "
                "How should a call that uses it be changed?")
    return f"In {lib}, the behavior of {fields[0]} changed. What argument or conversion keeps the old result?"


def main():
    rows = list(csv.DictReader(open(os.path.join(ROOT, "test_cases", "list.csv"), encoding="utf-8")))
    ids = [r["id"] for r in rows]
    assert set(ids) == set(SPEC), sorted(set(ids) ^ set(SPEC))
    kinds = {"removed API": "api", "removed parameter": "param", "behavior change (raises)": "behavior"}
    out = []
    for r in rows:
        assert kinds[r["change_type"]] == SPEC[r["id"]][0], r["id"]
        out.append(dict(id=r["id"], library=r["library"], change_type=r["change_type"],
                        question=question(r["id"], r["library"].lower()), recorded_fix=r["replacement"],
                        checked_by_hand="all answers" if r["id"] in REVIEW else "unclear answers"))
    path = os.path.join(HERE, "results", "questions.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(f"{len(out)} questions -> {os.path.abspath(path)}")
    for kind in ("api", "param", "behavior"):
        print(f"  {kind}: {sum(SPEC[r['id']][0] == kind for r in out)}")
    print(f"  checked by hand for every answer: {len(REVIEW)}")


if __name__ == "__main__":
    main()
