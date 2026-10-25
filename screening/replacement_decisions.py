"""Criterion 3 for the rows of the candidate pool: is there a documented, equivalent replacement?

Used by build_pool.py. A replacement counts as documented if the release notes, the NumPy 2.0
migration guide, or the old version's own deprecation warning or docstring give it
(results/<library>_deprecations.csv records the latter). As for the earlier candidates, removing an
argument counts as the replacement when the argument had no effect in the old version (for example
`errors` in `where`).

Keys: rows of the API comparison by "<defined_in>.<name>" or "<defined_in>.<name>(<parameter>)";
rows from the release notes by their entry.
Values: ("yes", replacement, source) or ("no", reason, source). Where neither the release notes nor
the old version's code gave the replacement, the old code was run and its deprecation warning read
(results/pool_checks.csv, column old_warnings).
"""

RN_P = "pandas 2.0.0 release notes"
RN_N = "NumPy {} release notes"
GUIDE = "NumPy 2.0 migration guide"
WARN = "deprecation warning in the old version"
DOC = "docstring in the old version"

D = {}


def add(keys, decision, text, source):
    for k in ([keys] if isinstance(keys, str) else keys):
        D[k] = (decision, text, source)


# ---------------- pandas: removed attributes ----------------
add(["BaseOffset.apply", "BaseOffset.apply_index"], "yes", "offset + other", WARN)
add("BaseOffset.isAnchored", "yes", "off.is_anchored()", WARN)
add("BaseOffset.onOffset", "yes", "off.is_on_offset(ts)", WARN)
add(["BaseWindow.is_datetimelike", "BaseWindow.validate"], "no", "removed without a replacement", WARN)
add(["Categorical.is_dtype_equal", "CategoricalIndex.is_dtype_equal"], "no", "removed without a replacement", WARN)
add("Categorical.replace", "yes", "pd.Series(cat).replace(...)", RN_P + ", line 961")
add("Categorical.take_nd", "yes", "cat.take(...)", WARN)
add("CategoricalIndex.take_nd", "yes", "idx.take(...)", WARN)
add(["DataFrameGroupBy.mad", "SeriesGroupBy.mad"], "yes", "(x - x.mean()).abs().mean() for each group", WARN)
add(["DataFrameGroupBy.tshift", "SeriesGroupBy.tshift"], "yes", "gb.shift(periods, freq=freq)", DOC)
add("DatetimeArray.to_perioddelta", "yes", "arr - arr.to_period(freq).to_timestamp()", WARN)
add(["DatetimeArray.week", "DatetimeArray.weekofyear", "DatetimeIndex.weekofyear",
     "DatetimeProperties.weekofyear"], "yes", "obj.isocalendar().week", RN_P + ", line 862")
add("DatetimeIndexOpsMixin.inferred_freq", "no", "not in the release notes, and the old version gives no replacement", "")
add(["DatetimeTimedeltaMixin.is_type_compatible", "Index.is_type_compatible"], "no",
    "removed without a replacement", RN_P + ", line 849")
add("ExponentialMovingWindow.vol", "yes", "ewm.std(...)", WARN)
add(["GroupBy.backfill", "Resampler.backfill"], "yes", "obj.bfill(...)", WARN)
add("Resampler.pad", "yes", "r.ffill(...)", WARN)
add("Index.get_value", "yes", "series[key]", WARN)
add("Index.set_value", "no", "removed without a replacement", WARN)
add("MultiIndex.is_lexsorted", "yes", "mi.is_monotonic_increasing", WARN)
add("MultiIndex.lexsort_depth", "no", "the given replacement is_monotonic_increasing returns a bool, not the depth",
    WARN)
add(["NaTType.freq", "_Timedelta.delta", "_Timedelta.freq", "_Timedelta.is_populated", "_Timestamp.freq"],
    "no", "removed without a replacement", WARN)
add("pandas.SparseArray", "yes", "pd.arrays.SparseArray", WARN)
add("pandas.datetime", "yes", "from datetime import datetime", WARN)
add("pandas.np", "yes", "import numpy as np", WARN)
add("pandas.api.types.is_extension_type", "yes", "pd.api.types.is_extension_array_dtype", WARN)
add("pandas.errors.AccessorRegistrationWarning", "no", "removed without a replacement", "")

# ---------------- pandas: removed parameters ----------------
add([f"{c}.factorize(na_sentinel)" for c in ("ArrowExtensionArray", "BaseMaskedArray", "ExtensionArray",
                                             "IndexOpsMixin", "RangeIndex", "SparseArray", "TimelikeOps")],
    "yes", "use_na_sentinel=True instead of na_sentinel=-1", WARN + " (as for P39)")
add([f"Categorical.{m}(inplace)" for m in ("add_categories", "as_ordered", "as_unordered", "remove_categories",
                                           "remove_unused_categories", "rename_categories", "reorder_categories",
                                           "set_ordered")],
    "yes", "cat = cat.<method>(...)", RN_P + ", line 1004 (as for P38)")
add(["MultiIndex.set_codes(inplace)", "MultiIndex.set_levels(inplace)"], "yes", "mi = mi.<method>(...)",
    RN_P + ", line 890")
add([f"{c}.{m}(level)" for c in ("DataFrame", "Series")
     for m in ("all", "any", "count", "kurt", "kurtosis", "max", "mean", "median", "min", "prod", "product",
               "sem", "skew", "std", "sum", "var")],
    "yes", "obj.groupby(level=...).<method>()", RN_P + ", line 958 (as for P30)")
add(["DataFrame.mask(errors)", "DataFrame.where(errors)", "Series.mask(errors)"], "yes",
    "remove the errors argument (it had no effect)", RN_P + ", line 912 (as for P40)")
add(["DataFrame.mask(try_cast)", "DataFrame.where(try_cast)", "Series.mask(try_cast)", "Series.where(try_cast)"],
    "yes", "remove the try_cast argument (it had no effect)", RN_P + ", line 898")
add(["DataFrame.resample(base)", "DataFrame.resample(loffset)"], "yes", "offset= or origin=",
    RN_P + ", line 1036 (as for P34, P35)")
add([f"{c}.get_loc({p})" for c in ("DatetimeIndex", "IntervalIndex", "MultiIndex", "PeriodIndex", "RangeIndex",
                                   "TimedeltaIndex", "Index") for p in ("method", "tolerance")],
    "yes", "idx.get_indexer([key], method=..., tolerance=...)[0]", RN_P + ", line 978 (as for P43)")
add([f"{c}.{m}(kind)" for c in ("DatetimeIndex", "Index", "MultiIndex")
     for m in ("slice_indexer", "get_slice_bound", "slice_locs")],
    "yes", "remove the kind argument (it had no effect)", RN_P + ", line 902")
add(["DatetimeTZDtype.type(freq)", "Timestamp.fromordinal(freq)"], "no",
    "removed without a replacement (as for P19)", RN_P + ", line 838")
add(["Expanding.quantile(quantile)", "Rolling.quantile(quantile)"], "yes", "q=...",
    "deprecation warning in the new version")
add(["Index.copy(names)", "RangeIndex.copy(names)"], "yes", "idx.copy(name=...)", WARN)
add("MultiIndex.copy(codes)", "yes", "mi.copy().set_codes(...)", WARN)
add("MultiIndex.copy(levels)", "yes", "mi.copy().set_levels(...)", WARN)
add(["MultiIndex.copy(dtype)", "RangeIndex.copy(dtype)"], "yes", "idx.copy().astype(...)", WARN + " (as for P24)")
add("NDArrayBackedExtensionArray.shift(axis)", "yes", "remove the axis argument (it had no effect on 1-D arrays)", "")
add("NDFrame.between_time(include_start)", "yes", "inclusive=...", RN_P + ", line 974 (as for P36)")
add(["NDFrame.take(is_copy)", "Series.take(is_copy)"], "yes", "remove the is_copy argument (it had no effect)",
    WARN)
add("PeriodIndex.astype(how)", "yes", "idx.to_timestamp(how=...)", RN_P + ", line 897")
add("Series.groupby(squeeze)", "yes", "remove the squeeze argument", RN_P + ", line 886 (as for P21)")
add("Series.set_axis(inplace)", "yes", "s = s.set_axis(...)", RN_P + ", line 893 (as for P23)")
add("pandas.bdate_range(closed)", "yes", "inclusive=...", RN_P + ", line 975 (as for P37)")
add("pandas.eval(truediv)", "yes", "remove the truediv argument (it had no effect)", WARN)
add("pandas.infer_freq(warn)", "yes", "remove the warn argument (it had no effect)", DOC)
add("pandas.lreshape(label)", "yes", "remove the label argument (it was not used)", DOC)
add(["pandas.read_csv(mangle_dupe_cols)", "pandas.read_table(mangle_dupe_cols)"], "yes",
    "remove the argument (only True was supported)", RN_P + ", line 911")
add(["pandas.read_csv(warn_bad_lines)", "pandas.read_table(warn_bad_lines)", "pandas.read_table(error_bad_lines)"],
    "yes", "on_bad_lines=...", RN_P + ", line 903 (as for P32)")
add("pandas.read_table(prefix)", "yes", "rename the columns after reading", RN_P + ", line 903 (as for P33)")
add("pandas.read_table(squeeze)", "yes", "call .squeeze('columns') on the result", RN_P + ", line 903 (as for P31)")
add("pandas.read_json(numpy)", "no", "removed without a replacement", RN_P + ", line 969")
add("pandas.arrays.SparseArray(index)", "yes", "np.full(len(index), value) passed as data", WARN)
add([f"pandas.testing.{f}(check_less_precise)" for f in ("assert_extension_array_equal", "assert_frame_equal",
                                                        "assert_index_equal", "assert_series_equal")],
    "yes", "stop passing check_less_precise", WARN)

# ---------------- NumPy: removed attributes and parameters ----------------
add("finfo.machar", "no", "removed without a replacement", RN_N.format("1.25.0") + ", line 110")
add(["generic.itemset", "ndarray.itemset"], "yes", "arr[index] = value",
    GUIDE + ", ndarray and scalar methods (listed as setitem)")
add("generic.newbyteorder", "yes", "x.view(x.dtype.newbyteorder(order))", GUIDE + ", ndarray and scalar methods")
add("generic.ptp", "yes", "np.ptp(x)", GUIDE + ", ndarray and scalar methods")
add([f"numpy.{n}" for n in ("ALLOW_THREADS", "BUFSIZE", "CLIP", "WRAP", "RAISE", "MAXDIMS", "MAY_SHARE_BOUNDS",
                            "MAY_SHARE_EXACT", "FLOATING_POINT_SUPPORT", "FPE_DIVIDEBYZERO", "FPE_INVALID",
                            "FPE_OVERFLOW", "FPE_UNDERFLOW", "UFUNC_BUFSIZE_DEFAULT", "UFUNC_PYVALS_NAME")],
    "no", "the guide gives no replacement", GUIDE + ", main namespace")
add([f"numpy.{n}" for n in ("ERR_CALL", "ERR_DEFAULT", "ERR_IGNORE", "ERR_LOG", "ERR_PRINT", "ERR_RAISE", "ERR_WARN",
                            "SHIFT_DIVIDEBYZERO", "SHIFT_INVALID", "SHIFT_OVERFLOW", "SHIFT_UNDERFLOW")],
    "no", "removed without a replacement", RN_N.format("2.0.0") + ", line 156")
add([f"numpy.{n}" for n in ("ComplexWarning", "ModuleDeprecationWarning", "RankWarning", "TooHardError")],
    "yes", "np.exceptions.<name>", RN_N.format("2.0.0") + ", line 152 (as for N37, N38)")
add("numpy.MachAr", "no", "removed without a replacement", WARN)
add("numpy.DataSource", "yes", "np.lib.npyio.DataSource", GUIDE + ", main namespace")
add("numpy.Infinity", "yes", "np.inf", GUIDE + ", main namespace")
add("numpy.NAN", "no", "not in the guide, which calls such removed members private", GUIDE + ", main namespace")
add("numpy.NZERO", "yes", "-0.0", GUIDE + ", main namespace")
add("numpy.PINF", "yes", "np.inf", GUIDE + ", main namespace")
add("numpy.PZERO", "yes", "0.0", GUIDE + ", main namespace")
add([f"numpy.{n}" for n in ("bool8", "bytes0", "int0", "object0", "str0", "uint0", "void0")], "no",
    "deprecated and removed without a replacement", RN_N.format("1.24.0") + ", Deprecations")
add("numpy.clongfloat", "yes", "np.clongdouble", GUIDE + ", main namespace")
add("numpy.longcomplex", "yes", "np.clongdouble", GUIDE + ", main namespace")
add("numpy.singlecomplex", "yes", "np.complex64", GUIDE + ", main namespace")
add("numpy.complex", "yes", "complex", WARN)
add("numpy.unicode", "yes", "str", WARN)
add("numpy.format_parser", "yes", "np.rec.format_parser", RN_N.format("2.0.0") + ", line 241")
add(["numpy.geterrobj", "numpy.seterrobj"], "no", "np.errstate is not an equivalent of the error object",
    RN_N.format("2.0.0") + ", line 131")
add("numpy.issctype", "yes", "issubclass(rep, np.generic)", GUIDE + ", main namespace")
add("numpy.maximum_sctype", "no", "the guide says to choose a dtype explicitly", GUIDE + ", main namespace")
add("numpy.lookfor", "no", "the guide says to search the documentation", GUIDE + ", main namespace")
add("numpy.msort", "yes", "np.sort(a, axis=0)", RN_N.format("2.0.0") + ", line 385")
add("numpy.set_numeric_ops", "no", "the replacement is in the C API", GUIDE + ", main namespace")
add("numpy.source", "yes", "print(inspect.getsource(obj)); the old output also starts with an 'In file:' line",
    RN_N.format("2.0.0") + ", line 140")
add("numpy.tracemalloc_domain", "yes", "np.lib.tracemalloc_domain", RN_N.format("2.0.0") + ", line 207")
add("numpy.typeDict", "yes", "np.sctypeDict", WARN)
add("numpy.use_hugepage", "no", "not in the guide, which calls such removed members private", GUIDE)
add(["numpy.histogram2d(normed)", "numpy.histogramdd(normed)"], "yes", "density=...",
    RN_N.format("1.24.0") + ", line 82 (as for N34)")
add([f"numpy.testing.{f}({p})" for f in ("assert_array_equal", "assert_array_almost_equal") for p in ("x", "y")],
    "no", "the keyword names changed without a documented replacement", "")

# ---------------- release-note entries ----------------
add("pandas-2.0.0-L733", "yes", "pass the arguments by keyword", RN_P)
add(["pandas-2.0.0-L734", "pandas-2.0.0-L777", "pandas-2.0.0-L782", "pandas-2.0.0-L895", "pandas-2.0.0-L909",
     "pandas-2.0.0-L952", "pandas-2.0.0-L971", "pandas-2.0.0-L982", "pandas-2.0.0-L998", "pandas-2.0.0-L999",
     "pandas-2.0.0-L1000", "pandas-2.0.0-L1016", "pandas-2.0.0-L1043", "pandas-2.0.0-L1044", "pandas-2.2.0-L508"],
    "no", "no replacement that gives the old result", RN_P)
add("pandas-2.0.0-L739", "yes", "obj.astype('int64', copy=False).astype(dtype)", RN_P)
add(["pandas-2.0.0-L755", "pandas-2.0.0-L1026"], "yes", "remove the dtype argument (the old version ignored it)",
    RN_P)
add("pandas-2.0.0-L1033", "yes", "call Series(arr) without passing a dtype", WARN)
add(["pandas-2.0.0-L875", "pandas-2.0.0-L876"], "yes", "pd.Series(values).dt.tz_localize(None)", WARN)
add(["pandas-2.0.0-L878", "pandas-2.0.0-L997", "pandas-2.0.0-L1050"], "no", "no replacement is given", RN_P)
add("pandas-2.0.0-L907", "yes", "the specific Index subclass, for example pd.DatetimeIndex(..., tz=...)", WARN)
add("pandas-2.0.0-L953", "yes", "[value] instead of the scalar", WARN)
add("pandas-2.0.0-L954", "yes", "pd.CategoricalIndex([], ...)", WARN)
add("pandas-2.0.0-L985", "yes", "fill_value=pd.Timestamp(...)", WARN)
add("pandas-2.0.0-L986", "yes", "pass the column itself into times", WARN)
add("pandas-2.0.0-L991", "yes", "s[s.index.isin(sequence, level=1)]", WARN)
add("pandas-2.0.0-L1003", "yes", "cat = cat.rename_categories(...)", WARN)
add("pandas-2.0.0-L1009", "yes", "None instead of a negative number", WARN)
add("pandas-2.0.0-L1034", "yes", "pd.Series(values).astype(dtype)", WARN)
add("pandas-2.0.0-L1048", "yes", "convert to a suitable dtype before diff", WARN)
add("pandas-2.0.0-L1049", "yes", "convert the DataFrame with .to_numpy() first", WARN)
add("pandas-2.0.0-L877", "yes", "pass {name: data[name] for name in data.dtype.names}", RN_P)
add("pandas-2.0.0-L879", "yes", "obj.tz_localize(tz) / ser.dt.tz_localize(tz)", RN_P)
add("pandas-2.0.0-L880", "yes", "obj.tz_localize(None)", RN_P)
add("pandas-2.0.0-L881", "no", "a non-boolean sort was used by its truth value; no replacement is given", RN_P)
add("pandas-2.0.0-L887", "yes", "offset + other", WARN)
add(["pandas-2.0.0-L894", "pandas-2.0.0-L921", "pandas-2.0.0-L1068"], "yes", "pass the arguments by keyword", RN_P)
add("pandas-2.0.0-L899", "yes", "obj.to_timestamp(...).tz_localize(tz)", RN_P)
add("pandas-2.0.0-L906", "yes", "pass a tuple as the key", RN_P)
add([f"pandas-2.0.0-L{n}" for n in list(range(914, 921)) + list(range(922, 933)) + [934, 935, 936, 937, 938, 939]
     + list(range(941, 952))],
    "yes", "pass the arguments by keyword", RN_P)
add("pandas-2.0.0-L962", "yes", "skipna=...", RN_P)
add("pandas-2.0.0-L970", "yes", "the full name of the orient", RN_P)
add("pandas-2.0.0-L987", "yes", "inclusive='both' / 'neither'", RN_P)
add("pandas-2.0.0-L988", "yes", "remove the out-of-bounds indices (the old version ignored them)", RN_P)
add("pandas-2.0.0-L990", "yes", "pass a list of column labels", WARN)
add("pandas-2.0.0-L992", "yes", "use .iloc with positions", RN_P)
add("pandas-2.0.0-L993", "yes", "cast the key to int", RN_P)
add("pandas-2.0.0-L994", "yes", "use .loc", RN_P)
add("pandas-2.0.0-L995", "yes", "pass a list instead of a set", WARN)
add("pandas-2.0.0-L996", "yes", "convert to numpy before indexing", RN_P)
add("pandas-2.0.0-L1006", "yes", "path=...", RN_P)
add("pandas-2.0.0-L1007", "yes", "pass the slice directly", RN_P)
add("pandas-2.0.0-L1008", "yes", "frame.loc[key]", RN_P)
add("pandas-2.0.0-L1010", "yes", "remove the option (it had no effect on to_string or repr)", "")
add("pandas-2.0.0-L1024", "yes", "idx.intersection / union / symmetric_difference", WARN)
add("pandas-2.0.0-L1035", "yes", "values.view('int64')", RN_P)
add("pandas-2.0.0-L1041", "yes", "ts < pd.Timestamp(date)", WARN)
add("pandas-2.0.0-L1042", "no", "no replacement is given", WARN)
add("pandas-2.0.0-L1052", "yes", "left, right = left.align(right, axis=1, copy=False)", RN_P)
add(["pandas-2.0.0-L1053", "pandas-2.0.0-L1056", "pandas-2.0.0-L1057", "pandas-2.0.0-L1059", "pandas-2.0.0-L1060"],
    "yes", "numeric_only=True, or select the numeric columns", WARN + " (as for P45)")
add("pandas-2.0.0-L1065", "yes", "remove the extra arguments (they were not used)", RN_P)
add("numpy-1.24.0-L89", "yes", "dtype=object", RN_N.format("1.24.0"))
add("numpy-1.24.0-L113", "yes", "pass the dtype as a string or scalar type", RN_N.format("1.24.0"))
add(["numpy-1.24.0-L121", "numpy-1.25.0-L114", "numpy-1.25.0-L151", "numpy-1.25.0-L222", "numpy-2.0.0-L396",
     "numpy-2.0.0-L399", "numpy-2.0.0-L1235", "numpy-2.0.0-L1510", "numpy-2.1.0-L353", "numpy-2.1.0-L355"],
    "no", "no replacement that gives the old result", "NumPy release notes")
add("numpy-1.25.0-L119", "yes", "pass a list", RN_N.format("1.25.0"))
add("numpy-1.25.0-L124", "yes", "casting='unsafe'", WARN)
add("numpy-1.25.0-L206", "yes", "out=...", RN_N.format("1.25.0"))
add("numpy-2.0.0-L131", "no", "np.errstate is not an equivalent of extobj", RN_N.format("2.0.0"))
add("numpy-2.0.0-L246", "no", "removed without a replacement", RN_N.format("2.0.0"))
add("numpy-2.0.0-L410", "yes", "encoding='bytes'", RN_N.format("2.0.0"))
add("numpy-2.0.0-L454", "yes", "np.linalg.solve(a, b[..., None])[..., 0]", RN_N.format("2.0.0"))
add("numpy-2.0.0-L1407", "yes", "axis=None", RN_N.format("2.0.0"))
add("numpy-2.0.0-L1420", "yes", "np.asarray(...)", GUIDE + ", Adapting to changes in the copy keyword")
add("numpy-2.1.0-L52", "yes", "np.atleast_1d(x).nonzero()", WARN)
add("numpy-2.1.0-L340", "yes", "pass a NumPy scalar or array", RN_N.format("2.1.0"))
