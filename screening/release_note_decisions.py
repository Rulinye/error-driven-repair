"""Decision on each release-note entry: does it add a row to the candidate pool?

usage: python screening/release_note_decisions.py
Reads results/release_note_entries.csv and writes results/release_note_decisions.csv.

Categories
  api           the change is already a row of the API comparison
  api+removal   part of the entry is a row of the API comparison, part is a removal the comparison misses
  removal       a removal the API comparison misses (adds a pool row)
  raises        a behavior change that makes code that ran in the old version raise (adds a pool row)
  silent        a behavior change without an error (no pool row: silent changes are not test cases)
  out_of_scope  concerns an object outside the scope of the API comparison (no pool row)
  other         not a change that breaks running user code: build, dependencies, C API, platform,
                new capability, only the type of an existing error changes, or the old code still
                runs with a warning (no pool row)
An entry that describes one change for several related objects (for example DataFrame.drop and
Series.drop) adds one pool row.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")

D = {}


def add(release, lines, category, note):
    for line in ([lines] if isinstance(lines, int) else lines):
        D[(release, line)] = (category, note)


# ---------------- pandas 2.0.0: Notable bug fixes, Backwards incompatible API changes ----------------
P = "pandas 2.0.0"
add(P, 304, "silent", "groupby cumsum/cumprod now overflow instead of casting to float")
add(P, 334, "silent", "groupby nth now returns a filtration; result shape changes, no error")
add(P, 393, "raises", "constructing with an unsupported datetime64/timedelta64 resolution raises (P49)")
add(P, 436, "silent", "value_counts result named 'count' (P46)")
add(P, 466, "raises", "astype to an unsupported datetime64 unit raises (P50)")
add(P, 550, "silent", "UTC uses datetime.timezone.utc instead of pytz.UTC")
add(P, 584, "silent", "empty Series/DataFrame get a RangeIndex (P52)")
add(P, 613, "api", "to_latex(col_space) is a row; to_latex now needs jinja2")
add(P, [627, 628, 629, 633], "removal", "display.latex.* options removed in favor of styler.* options")
add(P, 634, "silent", "display.max_rows/max_columns no longer affect to_latex; the options remain")
add(P, [640, 641, 642, 643], "silent", "to_latex defaults changed")
add(P, 653, "other", "minimum versions of dependencies")
add(P, 692, "raises", "to_datetime uses one format for all elements; mixed formats raise (P47)")
add(P, 733, "raises", "freq, tz, nanosecond, unit of the Timestamp constructor are keyword-only")
add(P, 734, "raises", "Timestamp with nanosecond outside 0-999 raises")
add(P, 735, "other", "read_csv raises ParserError instead of IndexError; the old code also raised")
add(P, 736, "silent", "get_dummies returns bool instead of uint8 (P48)")
add(P, 737, "silent", "astype to datetime64[s/ms/us] keeps the unit")
add(P, 738, "silent", "astype to timedelta64[s/ms/us] keeps the unit instead of float (P51)")
add(P, 739, "raises", "astype of datetime-like data to integer dtypes other than int64 raises")
add(P, 740, "other", "Index.astype from float to datetime-like now allowed; new capability")
add(P, [741, 742, 743, 744, 745, 746], "silent", "non-nanosecond resolutions are kept")
add(P, 747, "silent", "default of other in mask changed")
add(P, 748, "silent", "quantile keeps the sparse dtype")
add(P, 749, "silent", "object Index of datetimes no longer converted to DatetimeIndex")
add(P, 750, "out_of_scope", "pandas.testing.assert_index_equal")
add(P, 751, "silent", "Series.unique returns DatetimeArray/TimedeltaArray instead of ndarray")
add(P, 752, "other", "to_datetime accepts mixed datetime and numeric entries; new capability")
add(P, 753, "silent", "is_string_dtype returns True in fewer cases")
add(P, 754, "silent", "datetime and date objects give object dtype")
add(P, 755, "raises", "unparsable strings with dtype datetime64[ns] raise instead of giving object dtype")
add(P, 756, "other", "TypeError instead of ValueError; the old code also raised")
add(P, 757, "silent", "Index of NaT and None infers datetime64[ns]")
add(P, 758, "silent", "read_stata returns a RangeIndex")
add(P, 759, "silent", "object-dtype arithmetic no longer infers result types")
add(P, 760, "silent", "Index of all-bool objects keeps object dtype")
add(P, 761, "silent", "astype of bytes to string decodes")
add(P, 762, "silent", "'None' added to default na_values of read_csv")
add(P, 763, "raises", "integer dtype with non-round floats raises (P53)")
add(P, 764, "silent", "shift(axis=1) with integer fill_value")
add(P, 765, "other", "read_json closes files on error")
add(P, 766, "silent", "readers return a RangeIndex for empty results")
add(P, 767, "silent", "no silent consolidation; performance only")
add(P, 768, "silent", "df.loc[:, :] returns a new object")
add(P, 772, "silent", "constructors return a shallow copy")
add(P, 777, "raises", "cumprod of Timedelta data raises")
add(P, 778, "silent", "HDFStore returns a RangeIndex")
add(P, 779, "other", "ValueError instead of TypeError; the old code also raised")
add(P, 780, "silent", "read_json renames duplicate columns")
add(P, 781, "silent", "sparse from_coo levels int32")
add(P, 782, "raises", "to_datetime with unit 'Y' or 'M' and non-round floats raises")
add(P, 783, "silent", "methods return new objects")
add(P, 784, "silent", "aggregations of object columns no longer infer dtypes")
add(P, 785, "silent", "ArrowDtype division by zero")
add(P, 786, "other", "new function is_any_real_numeric_dtype")
add(P, [787, 788], "silent", "ArrowExtensionArray result types")
add(P, 789, "silent", "factorize/unique keep non-nanosecond units")

# ---------------- pandas 2.0.0: Removal of prior version deprecations/changes ----------------
add(P, 837, "api", "Int64Index, UInt64Index, Float64Index (P05-P07)")
add(P, 838, "api", "Timestamp.freq, Timestamp.freqstr, Timestamp(freq) (P19, P60)")
add(P, 839, "other", "internal Block classes")
add(P, 840, "removal", "option use_inf_as_null (P57)")
add(P, [841, 842], "other", "private modules under pandas.core")
add(P, 843, "out_of_scope", "pandas.io.json.json_normalize; module outside the scope (P55)")
add(P, [844, 845, 846, 847, 848, 849, 850, 851, 852], "api", "removed Categorical/Index members")
add(P, [853, 854], "silent", "values interpreted differently")
add(P, 855, "other", "private attributes")
add(P, [856, 857, 858, 859, 860, 861, 862, 864], "api", "removed members (P01-P04, P08, P11, P12, P15, P18, P54)")
add(P, 863, "other", "private attributes")
add(P, [865, 866, 867, 868, 870], "out_of_scope", "Styler")
add(P, 869, "api", "to_latex(col_space)")
add(P, 871, "out_of_scope", "pandas.testing")
add(P, [872, 873, 874], "api", "info(null_counts), is_monotonic, is_all_dates (P09, P10, P17, P20)")
add(P, [875, 876], "raises", "timezone-aware values with dtype datetime64[ns] raise")
add(P, 877, "raises", "MaskedRecords in the DataFrame constructor raise")
add(P, 878, "raises", "astype to unit-less datetime64 raises")
add(P, [879, 880], "raises", "astype between naive and timezone-aware datetime64 raises")
add(P, 881, "raises", "concat with a non-boolean sort raises")
add(P, 882, "out_of_scope", "pandas.io.date_converters")
add(P, 885, "out_of_scope", "SparseArray constructor")
add(P, 886, "api", "groupby(squeeze) (P21)")
add(P, 887, "out_of_scope", "DateOffset members")
add(P, [888, 889, 890, 891], "api", "to_series(keep_tz), copy(dtype/names), set_levels(inplace), to_excel (P24, P25)")
add(P, 892, "removal", "to_csv(line_terminator); the old signature already shows only lineterminator (P22)")
add(P, 893, "api", "set_axis(inplace) (P23)")
add(P, 894, "raises", "positional arguments to MultiIndex.set_levels/set_codes raise")
add(P, 895, "raises", "Timedelta strings with units Y, y or M raise")
add(P, [896, 897, 898], "api", "is_lexsorted, astype(how), where/mask(try_cast)")
add(P, 899, "removal", "Period.to_timestamp(tz); not visible in the Cython signature")
add(P, 900, "out_of_scope", "plotting")
add(P, [901, 902, 903, 904, 905], "api", "take(is_copy), kind, read_csv/read_excel arguments, describe (P31-P33, P41)")
add(P, 906, "raises", "a list key to xs raises")
add(P, 907, "raises", "subclass-specific keywords in the Index constructor raise")
add(P, 908, "api", "remove_unused_categories(inplace)")
add(P, 909, "raises", "Timestamp with unit 'M' or 'Y' and non-round floats raises")
add(P, [910, 911, 912], "api", "read_excel/read_csv(mangle_dupe_cols), where/mask(errors) (P40)")
add(P, list(range(913, 921)) + list(range(922, 952)), "raises", "positional (non-keyword) arguments raise")
add(P, 921, "out_of_scope", "ExtensionArray.argsort")
add(P, 952, "raises", "Index.reindex with a non-unique Index raises")
add(P, 953, "raises", "Categorical from scalar data raises")
add(P, 954, "raises", "CategoricalIndex without data raises")
add(P, [955, 956, 957], "api", "Rolling.validate, win_type, is_datetimelike")
add(P, 958, "api", "level keyword in aggregations (P30)")
add(P, 959, "api", "Timedelta.delta, is_populated, freq")
add(P, 960, "out_of_scope", "NaT.freq")
add(P, 961, "api", "Categorical.replace")
add(P, 962, "removal", "Categorical.min/max(numeric_only); not visible in the signature")
add(P, 963, "silent", "mean/median keep datetime-like columns")
add(P, [964, 965, 966, 967, 968, 969], "api", "is_extension_type, vol, get/set_value, slice_shift, pad, read_json(numpy) (P29, P44)")
add(P, 970, "raises", "abbreviated orient in to_dict raises")
add(P, 971, "raises", "partial slicing on a non-monotonic DatetimeIndex with missing keys raises KeyError")
add(P, 972, "out_of_scope", "pandas.tseries.frequencies.get_offset")
add(P, [973, 974, 975, 976, 977, 978, 979, 980], "api",
    "infer_freq(warn), between_time, date_range(closed), expanding(center), eval(truediv), get_loc, "
    "pd.datetime, pd.np (P36, P37, P42, P43)")
add(P, 981, "out_of_scope", "pandas.util.testing")
add(P, 982, "raises", "iterating over Series.str raises")
add(P, 983, "api", "pd.SparseArray")
add(P, 984, "other", "SparseSeries/SparseDataFrame were already unusable in pandas 1.5.3")
add(P, 985, "raises", "integer fill_value to shift with datetime-like dtypes raises")
add(P, 986, "raises", "a string column label as times in ewm raises")
add(P, 987, "raises", "True/False as inclusive in Series.between raises")
add(P, 988, "raises", "out-of-bounds usecols in read_csv raises")
add(P, 989, "out_of_scope", "ExcelWriter")
add(P, list(range(990, 1001)), "raises", "indexing, merge and melt cases that now raise")
add(P, 1001, "raises", "showindex in to_markdown raises")
add(P, 1002, "other", "setting a private attribute")
add(P, 1003, "raises", "setting Categorical.categories raises")
add(P, 1004, "api", "inplace in Categorical methods (P38)")
add(P, 1005, "silent", "Rolling.count default min_periods")
add(P, 1006, "removal", "fname renamed to path in to_parquet, to_stata, to_feather")
add(P, 1007, "raises", "a single-item list containing a slice as a Series key raises")
add(P, 1008, "raises", "a date string on a DataFrame selects a column; the old row slice raises KeyError")
add(P, 1009, "raises", "negative display.max_colwidth raises")
add(P, 1010, "removal", "option display.column_space")
add(P, [1011, 1012], "api", "mad, tshift (P26-P28)")
add(P, [1013, 1014, 1015], "silent", "default dtype of empty Series, set operations, to_datetime('now')")
add(P, 1016, "raises", "indexing aware/naive DatetimeIndex with the other kind raises KeyError")
add(P, 1017, "silent", "reindex with a date fill_value")
add(P, 1018, "out_of_scope", "SparseArray.astype")
add(P, list(range(1019, 1024)) + [1025], "silent", "result types or values differ")
add(P, 1024, "raises", "Index &, |, ^ are logical operations; non-boolean indexes can raise (to be checked)")
add(P, 1026, "raises", "DataFrame constructor with a dtype the data cannot be cast to raises")
add(P, list(range(1027, 1033)), "silent", "constructors and Timestamp interpret values differently")
add(P, [1033, 1034, 1035], "raises", "integer dtype with NaN, too large values or datetime64 values raises")
add(P, 1036, "api", "resample(base/loffset) (P34, P35)")
add(P, 1037, "other", "fillna now casts to object instead of raising; the old code raised")
add(P, [1038, 1039, 1040], "silent", "str.replace regex default, bool_only, axis=None")
add(P, [1041, 1042], "raises", "inequality comparison of Timestamp/NaT with date raises")
add(P, [1043, 1044], "raises", "transform/apply with list-likes raise instead of dropping columns")
add(P, 1045, "raises", "to_latex now needs jinja2")
add(P, 1046, "silent", "setitem with an integer key on a Float64Index")
add(P, 1047, "api", "factorize(na_sentinel) (P39)")
add(P, [1048, 1049, 1050], "raises", "diff on extension dtypes, outer ufuncs, numeric_only=True on non-numeric Series raise")
add(P, 1051, "silent", "groupby apply respects group_keys")
add(P, 1052, "raises", "comparing a misaligned DataFrame and Series raises")
add(P, [1053, 1054], "raises", "numeric_only defaults to False; non-numeric columns raise (P45)")
add(P, 1055, "silent", "Series.rank numeric_only default")
add(P, [1056, 1057, 1059, 1060], "raises", "nuisance columns in groupby/resample/rolling raise")
add(P, [1058, 1061, 1062], "silent", "setting in place, transform alignment, keys as tuples")
add(P, [1063, 1064], "out_of_scope", "ExcelWriter")
add(P, 1065, "raises", "extra *args/**kwargs in rolling/expanding/ewm ops raise")
add(P, 1066, "removal", "to_csv(line_terminator); same change as line 892")
add(P, 1067, "api", "lreshape(label)")
add(P, 1068, "raises", "positional arguments after expr in eval/query raise")
add(P, [1069, 1070], "other", "private or special methods")
add(P, 1071, "silent", "DataFrame.value_counts index type")

# ---------------- pandas 2.1.0, 2.2.0 ----------------
add("pandas 2.1.0", [288, 293], "other", "minimum versions of Python and dependencies")
add("pandas 2.1.0", 368, "other", "PandasArray renamed; the old name still works")
add("pandas 2.2.0", [364, 375, 376, 377, 378, 408], "silent", "merge/join sort order and level order")
add("pandas 2.2.0", 441, "other", "minimum versions of dependencies")
add("pandas 2.2.0", 507, "silent", "hash values of nullable dtypes")
add("pandas 2.2.0", 508, "out_of_scope", "pandas.testing")

# ---------------- NumPy 1.24.0 ----------------
N = "numpy 1.24.0"
add(N, 82, "api", "histogram(normed) (N34)")
add(N, 89, "raises", "ragged array creation raises unless dtype=object")
add(N, [94, 96, 100, 201], "other", "build and platform support")
add(N, [104, 107, 500], "out_of_scope", "numpy.ma")
add(N, 113, "raises", "non-canonical dtype instances in ufunc dtype=/signature= raise")
add(N, 121, "raises", "comparison ufuncs accept only bool or object as dtype=")
add(N, 127, "api", "np.object, np.float, np.int, np.str, np.complex (N01-N05)")
add(N, [138, 154, 169, 479], "silent", "fill, casts, dtype identity, overflow reporting")
add(N, 192, "other", "BufferError instead of TypeError; the old code also raised")
add(N, 508, "other", "nditer allocates all operands; new capability")

# ---------------- NumPy 1.25.0 ----------------
N = "numpy 1.25.0"
add(N, 110, "out_of_scope", "np.core.machar and finfo.machar")
add(N, 114, "raises", "unary + on non-numeric arrays raises")
add(N, 119, "raises", "stacking functions require a sequence; generators raise")
add(N, 124, "raises", "np.clip uses same-kind casting; unsafe casts raise")
add(N, [129, 138, 143, 216, 237, 615], "silent", "results differ")
add(N, 134, "out_of_scope", "numpy.dual")
add(N, 151, "raises", "== and != on incompatible arrays raise instead of returning False")
add(N, [166, 194], "out_of_scope", "numpy.testing")
add(N, [200, 248, 288, 637, 649], "other", "environment variable, Cython, C API, build")
add(N, 206, "removal", "y= alias of out= in fix, isposinf, isneginf; not visible in the signature")
add(N, 222, "raises", "np.equal/not_equal between datetime and timedelta raises")
add(N, [229, 266], "other", "a different error type; the old code also raised")
add(N, 275, "other", "override mechanism for array-likes")

# ---------------- NumPy 2.0.0 ----------------
N = "numpy 2.0.0"
add(N, 131, "api+removal", "geterrobj/seterrobj are rows; the ufunc keyword extobj= is not")
add(N, [137, 140, 143, 147, 152, 156, 162], "api", "removed main-namespace members (N31, N37, N38)")
add(N, list(range(172, 199, 2)), "api", "removed aliases (N06-N13, N21, N26, N27)")
add(N, [200, 202, 204, 207, 209, 211, 215, 218, 223, 228, 230, 234, 237, 241], "api",
    "removed main-namespace members (N19, N22-N25, N28-N30, N18, N39)")
add(N, 246, "api+removal", "np.int0, np.bool8 etc. are rows; the dtype strings 'int0', 'bool8' etc. are not")
add(N, 251, "out_of_scope", "numpy.array_api")
add(N, [259, 1433], "other", "protocols for authors of array-like classes")
add(N, [360, 365, 377, 381, 401], "other", "private modules and C API")
add(N, [371, 379, 385], "api", "set_numeric_ops, fastCopyAndTranspose, msort")
add(N, 391, "silent", "np.dtype(('f8', 1)) returns a subarray dtype")
add(N, 396, "raises", "assigning to ndarray.data raises")
add(N, 399, "raises", "binary_repr with a too small width raises")
add(N, 410, "raises", "loadtxt/genfromtxt pass str to converters; converters expecting bytes raise")
add(N, [424, 431, 438], "other", "f2py")
add(N, [446, 464, 1230, 1238, 1249, 1256, 1265, 1285, 1294, 1301, 1447, 1466, 1477, 1488, 1499], "silent",
    "results, types or representations differ")
add(N, 454, "raises", "np.linalg.solve broadcasting changed; some shapes raise (to be checked)")
add(N, 1235, "raises", "entering the same np.errstate twice raises")
add(N, 1243, "api", "byte_bounds moved to np.lib.array_utils")
add(N, [1315, 1326], "other", "new keyword; warning type")
add(N, 1335, "other", "Windows only")
add(N, [1346, 1389, 1398], "other", "renamed private modules; the old names still work with a warning")
add(N, [1367, 1378, 1380, 1382, 1383], "other", "C-level definition of intp")
add(N, 1407, "raises", "an out-of-bound axis raises instead of meaning axis=None")
add(N, 1420, "raises", "np.array(..., copy=False) raises when a copy is needed")
add(N, [1424, 1425, 1426], "other", "part of the entry at line 1420")
add(N, 1510, "raises", "np.can_cast with a Python int, float or complex raises")

# ---------------- NumPy 2.1.0 ----------------
N = "numpy 2.1.0"
add(N, 52, "raises", "nonzero on scalars and 0-d arrays raises")
add(N, 56, "api", "set_string_function")
add(N, 307, "other", "typing stub")
add(N, [312, 317], "silent", "floor/ceil/trunc keep integer dtypes; ma.corrcoef")
add(N, 333, "other", "summary of the entries at lines 340-355")
add(N, [340, 353, 355], "raises", "np.copyto with values that do not fit raises")
add(N, [344, 347], "other", "a different error type, or no longer raises")

# ---------------- NumPy 2.0 migration guide ----------------
N = "numpy 2.0 migration guide"
add(N, [49, 51], "silent", "NEP 50 promotion of Python and NumPy scalars")
add(N, [402, 410, 417, 421, 425, 435], "other", "advice, pickles, and the copy keyword covered by NumPy 2.0.0 line 1420")


def main():
    with open(os.path.join(RESULTS, "release_note_entries.csv"), newline="", encoding="utf-8") as f:
        entries = list(csv.DictReader(f))
    out = os.path.join(RESULTS, "release_note_decisions.csv")
    missing, counts = [], {}
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["entry", "library", "release", "line", "category", "note", "candidates", "text"])
        for e in entries:
            key = (f"{e['library']} {e['release']}", int(e["line"]))
            if key not in D:
                missing.append(e["entry"])
                continue
            cat, note = D[key]
            counts[cat] = counts.get(cat, 0) + 1
            w.writerow([e["entry"], e["library"], e["release"], e["line"], cat, note, e["candidates"], e["text"]])
    unused = sorted(set(D) - {(f"{e['library']} {e['release']}", int(e["line"])) for e in entries})
    print(f"{len(entries) - len(missing)} of {len(entries)} entries decided -> {out}")
    for cat in ("api", "api+removal", "removal", "raises", "silent", "out_of_scope", "other"):
        print(f"  {cat:13s} {counts.get(cat, 0)}")
    if missing:
        print("  not decided:", " ".join(missing))
    if unused:
        print("  decisions without an entry:", unused)


if __name__ == "__main__":
    main()
