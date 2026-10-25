"""Old code and replacement for each pool row that passed criteria 1, 4 and 3 (criterion 2 and the
replacement check; run by run_pool_checks.py).

Keys as in replacement_decisions.py. Each entry:
  code  the old usage; it must set `result` (run in the old and in the new environment)
  alt   the documented replacement (run in the new environment)
  mode  "full" compares a Series together with its index; default compares values only

Every snippet starts with:  import io, datetime, functools, numpy as np, pandas as pd
"""

SETUP = "import io, datetime, functools, numpy as np, pandas as pd\n"

S3 = "s = pd.Series([1.0, 2.0, 3.0])\n"
DF = "df = pd.DataFrame({'a': [1, 2, 3], 'b': [4.0, 5.0, 6.0]})\n"
MI_S = "s = pd.Series([1.0, 2.0, 4.0], index=pd.MultiIndex.from_tuples([('a', 1), ('a', 2), ('b', 1)]))\n"
MI_DF = ("df = pd.DataFrame({'x': [1.0, 2.0, 4.0], 'y': [3.0, 5.0, 9.0]}, "
         "index=pd.MultiIndex.from_tuples([('a', 1), ('a', 2), ('b', 1)]))\n")
S_H = "s = pd.Series(range(6), index=pd.date_range('2020-01-01', periods=6, freq='H'))\n"
DF_H = "df = pd.DataFrame({'v': range(6)}, index=pd.date_range('2020-01-01', periods=6, freq='H'))\n"
S_D = "s = pd.Series([1.0, 2.0, 3.0], index=pd.date_range('2020-01-01', periods=3, freq='D'))\n"
DTI = "idx = pd.date_range('2020-01-01', periods=3, freq='D')\n"
MI = "mi = pd.MultiIndex.from_tuples([('a', 1), ('b', 2)])\n"
OFF = "off = pd.offsets.Day()\nts = pd.Timestamp('2020-01-01')\n"
CAT = "cat = pd.Categorical(['a', 'b', 'a'])\n"
FAC = "codes, uniques = obj.factorize(na_sentinel=-1)\nresult = (codes.tolist(), [str(u) for u in uniques])"
FAC_ALT = "codes, uniques = obj.factorize(use_na_sentinel=True)\nresult = (codes.tolist(), [str(u) for u in uniques])"
GB = "df = pd.DataFrame({'k': [1, 1, 2], 'v': [1.0, 4.0, 2.0]})\n"
GB_T = ("s = pd.Series([1.0, 2.0, 3.0], index=pd.date_range('2020-01-01', periods=3, freq='D'))\n"
        "gb = s.groupby([1, 1, 2])\n")

SPEC = {}


def add(key, code, alt, mode="values"):
    SPEC[key] = {"code": code, "alt": alt, "mode": mode}


# ---------------- pandas: removed attributes ----------------
add("BaseOffset.apply", OFF + "result = off.apply(ts)", OFF + "result = off + ts")
ME = "off = pd.offsets.MonthEnd()\nidx = pd.DatetimeIndex(['2020-01-15'])\n"
add("BaseOffset.apply_index", ME + "result = off.apply_index(idx)", ME + "result = off + idx")
add("BaseOffset.isAnchored", OFF + "result = off.isAnchored()", OFF + "result = off.is_anchored()")
add("BaseOffset.onOffset", OFF + "result = off.onOffset(ts)", OFF + "result = off.is_on_offset(ts)")
add("Categorical.is_dtype_equal", CAT + "result = cat.is_dtype_equal(pd.Categorical(['b', 'a']))",
    CAT + "result = cat.dtype == pd.Categorical(['b', 'a']).dtype")
add("CategoricalIndex.is_dtype_equal",
    "ci = pd.CategoricalIndex(['a', 'b'])\nresult = ci.is_dtype_equal(pd.CategoricalIndex(['b', 'a']))",
    "ci = pd.CategoricalIndex(['a', 'b'])\nresult = ci.dtype == pd.CategoricalIndex(['b', 'a']).dtype")
add("Categorical.replace", CAT + "result = cat.replace('a', 'c')", CAT + "result = pd.Series(cat).replace('a', 'c')")
add("Categorical.take_nd", CAT + "result = cat.take_nd([2, 1])", CAT + "result = cat.take([2, 1])")
add("CategoricalIndex.take_nd", "ci = pd.CategoricalIndex(['a', 'b', 'a'])\nresult = ci.take_nd([2, 1])",
    "ci = pd.CategoricalIndex(['a', 'b', 'a'])\nresult = ci.take([2, 1])")
add("DataFrameGroupBy.mad", GB + "result = df.groupby('k').mad()",
    GB + "result = df.groupby('k').agg(lambda x: (x - x.mean()).abs().mean())")
add("SeriesGroupBy.mad", GB + "result = df.groupby('k')['v'].mad()",
    GB + "result = df.groupby('k')['v'].agg(lambda x: (x - x.mean()).abs().mean())", "full")
add("DataFrameGroupBy.tshift", GB_T + "result = s.to_frame().groupby([1, 1, 2]).tshift(1, freq='D')",
    GB_T + "result = s.to_frame().groupby([1, 1, 2]).shift(1, freq='D')")
add("SeriesGroupBy.tshift", GB_T + "result = gb.tshift(1, freq='D')", GB_T + "result = gb.shift(1, freq='D')", "full")
ARR = "arr = pd.array(pd.date_range('2020-01-01 10:00', periods=3, freq='D'))\n"
add("DatetimeArray.to_perioddelta", ARR + "result = arr.to_perioddelta('D')",
    ARR + "result = arr - arr.to_period('D').to_timestamp()")
add("DatetimeArray.week", ARR + "result = list(arr.week)", ARR + "result = list(arr.isocalendar().week)")
add("DatetimeArray.weekofyear", ARR + "result = list(arr.weekofyear)", ARR + "result = list(arr.isocalendar().week)")
add("DatetimeIndex.weekofyear", DTI + "result = idx.weekofyear", DTI + "result = idx.isocalendar().week")
SDT = "s = pd.Series(pd.date_range('2020-01-01', periods=3, freq='D'))\n"
add("DatetimeProperties.weekofyear", SDT + "result = s.dt.weekofyear", SDT + "result = s.dt.isocalendar().week")
add("DatetimeIndexOpsMixin.inferred_freq", "pi = pd.period_range('2020-01', periods=3, freq='M')\nresult = pi.inferred_freq",
    "pi = pd.period_range('2020-01', periods=3, freq='M')\nresult = pi.freqstr")
add("ExponentialMovingWindow.vol", S3 + "result = s.ewm(com=1).vol()", S3 + "result = s.ewm(com=1).std()")
add("GroupBy.backfill", "df = pd.DataFrame({'k': [1, 1, 2], 'v': [None, 4.0, 2.0]})\nresult = df.groupby('k').backfill()",
    "df = pd.DataFrame({'k': [1, 1, 2], 'v': [None, 4.0, 2.0]})\nresult = df.groupby('k').bfill()")
add("Index.get_value", "s = pd.Series([1, 2], index=['a', 'b'])\nresult = s.index.get_value(s, 'b')",
    "s = pd.Series([1, 2], index=['a', 'b'])\nresult = s['b']")
add("MultiIndex.is_lexsorted", "mi = pd.MultiIndex.from_tuples([('a', 2), ('a', 1)])\nresult = mi.is_lexsorted()",
    "mi = pd.MultiIndex.from_tuples([('a', 2), ('a', 1)])\nresult = mi.is_monotonic_increasing")
add("Resampler.backfill", S_H + "result = s.resample('30min').backfill()", S_H + "result = s.resample('30min').bfill()",
    "full")
add("Resampler.pad", S_H + "result = s.resample('30min').pad()", S_H + "result = s.resample('30min').ffill()", "full")
add("pandas.SparseArray", "result = list(pd.SparseArray([0, 1, 0]))", "result = list(pd.arrays.SparseArray([0, 1, 0]))")
add("pandas.datetime", "result = pd.datetime(2020, 1, 2)", "result = datetime.datetime(2020, 1, 2)")
add("pandas.np", "result = pd.np.arange(3)", "result = np.arange(3)")
add("pandas.api.types.is_extension_type",
    "result = [pd.api.types.is_extension_type(x) for x in (pd.Series(pd.Categorical(['a'])), pd.Series([1]), "
    "pd.arrays.SparseArray([1]))]",
    "result = [pd.api.types.is_extension_array_dtype(x) for x in (pd.Series(pd.Categorical(['a'])), pd.Series([1]), "
    "pd.arrays.SparseArray([1]))]")

# ---------------- pandas: removed parameters ----------------
for key, obj in [("BaseMaskedArray", "pd.array([1, None, 1], dtype='Int64')"),
                 ("ExtensionArray", "pd.arrays.IntervalArray.from_breaks([0, 1, 2])"),
                 ("IndexOpsMixin", "pd.Series(['a', None, 'a'])"),
                 ("RangeIndex", "pd.RangeIndex(3)"),
                 ("SparseArray", "pd.arrays.SparseArray([1.0, np.nan, 1.0])"),
                 ("TimelikeOps", "pd.array(pd.to_datetime(['2020-01-01', None, '2020-01-01']))")]:
    add(f"{key}.factorize(na_sentinel)", f"obj = {obj}\n" + FAC, f"obj = {obj}\n" + FAC_ALT)

CAT_CASES = {
    "add_categories": ("['c']", "list(cat.categories)"),
    "as_ordered": ("", "cat.ordered"),
    "as_unordered": ("", "cat.ordered"),
    "remove_categories": ("['b']", "list(cat)"),
    "remove_unused_categories": ("", "list(cat.categories)"),
    "rename_categories": ("['x', 'y']", "list(cat)"),
    "reorder_categories": ("['b', 'a']", "list(cat.categories)"),
    "set_ordered": ("True", "cat.ordered"),
}
for m, (arg, res) in CAT_CASES.items():
    start = ("cat = pd.Categorical(['a', 'b', 'a'], categories=['a', 'b', 'c'], ordered=True)\n"
             if m in ("as_unordered", "remove_unused_categories") else CAT)
    sep = ", " if arg else ""
    add(f"Categorical.{m}(inplace)", start + f"cat.{m}({arg}{sep}inplace=True)\nresult = {res}",
        start + f"cat = cat.{m}({arg})\nresult = {res}")

AGG = ("all", "any", "count", "kurt", "kurtosis", "max", "mean", "median", "min", "prod", "product", "sem", "skew",
       "std", "sum", "var")
GB_NAME = {"product": "prod"}
for m in AGG:
    g = GB_NAME.get(m, m)
    # groupby has no kurt in pandas 2.2.3; following "use groupby instead", the method is applied per group
    g = f"agg(lambda x: x.{m}())" if m in ("kurt", "kurtosis") else f"{g}()"
    add(f"Series.{m}(level)", MI_S + f"result = s.{m}(level=0)", MI_S + f"result = s.groupby(level=0).{g}", "full")
    add(f"DataFrame.{m}(level)", MI_DF + f"result = df.{m}(level=0)", MI_DF + f"result = df.groupby(level=0).{g}")

add("DataFrame.mask(errors)", DF + "result = df.mask(df > 2, errors='ignore')", DF + "result = df.mask(df > 2)")
add("DataFrame.where(errors)", DF + "result = df.where(df > 2, errors='ignore')", DF + "result = df.where(df > 2)")
add("Series.mask(errors)", S3 + "result = s.mask(s > 2, errors='ignore')", S3 + "result = s.mask(s > 2)")
add("DataFrame.mask(try_cast)", DF + "result = df.mask(df > 2, try_cast=True)", DF + "result = df.mask(df > 2)")
add("DataFrame.where(try_cast)", DF + "result = df.where(df > 2, try_cast=True)", DF + "result = df.where(df > 2)")
add("Series.mask(try_cast)", S3 + "result = s.mask(s > 2, try_cast=True)", S3 + "result = s.mask(s > 2)")
add("Series.where(try_cast)", S3 + "result = s.where(s > 2, try_cast=True)", S3 + "result = s.where(s > 2)")
add("DataFrame.resample(base)", DF_H + "result = df.resample('2H', base=1).sum()",
    DF_H + "result = df.resample('2H', offset='1H').sum()")
add("DataFrame.resample(loffset)", DF_H + "result = df.resample('2H', loffset='1H').sum()",
    DF_H + "result = df.resample('2H').sum()\nresult.index = result.index + pd.Timedelta('1H')")

LOC = {
    "DatetimeIndex": ("idx = pd.date_range('2020-01-01', periods=3, freq='D')\nkey = pd.Timestamp('2020-01-02 10:00')\n",
                      "pd.Timedelta('1D')"),
    "TimedeltaIndex": ("idx = pd.timedelta_range('1 day', periods=3)\nkey = pd.Timedelta('2 days 10:00:00')\n",
                       "pd.Timedelta('1D')"),
    "PeriodIndex": ("idx = pd.period_range('2020-01-01', periods=3, freq='D')\nkey = pd.Period('2020-01-02', freq='D')\n",
                    "pd.Timedelta('1D')"),
    "RangeIndex": ("idx = pd.RangeIndex(0, 10, 2)\nkey = 3\n", "1"),
    "Index": ("idx = pd.Index([1, 5, 10])\nkey = 6\n", "2"),
}
for c, (setup, tol) in LOC.items():
    if c != "Index":
        add(f"{c}.get_loc(method)", setup + "result = idx.get_loc(key, method='nearest')",
            setup + "result = idx.get_indexer([key], method='nearest')[0]")
    add(f"{c}.get_loc(tolerance)", setup + f"result = idx.get_loc(key, method='nearest', tolerance={tol})",
        setup + f"result = idx.get_indexer([key], method='nearest', tolerance={tol})[0]")
II = "ii = pd.IntervalIndex.from_breaks([0, 1, 2])\n"
add("IntervalIndex.get_loc(method)", II + "result = ii.get_loc(1.5, method=None)", II + "result = ii.get_indexer([1.5])[0]")
add("IntervalIndex.get_loc(tolerance)", II + "result = ii.get_loc(1.5, tolerance=None)",
    II + "result = ii.get_indexer([1.5])[0]")
add("MultiIndex.get_loc(method)", MI + "result = mi.get_loc(('b', 2), method=None)",
    MI + "result = mi.get_indexer([('b', 2)])[0]")

SLC = "sl = {}\nresult = (sl.start, sl.stop, sl.step)"
add("DatetimeIndex.slice_indexer(kind)", DTI + SLC.format("idx.slice_indexer('2020-01-02', '2020-01-03', kind='loc')"),
    DTI + SLC.format("idx.slice_indexer('2020-01-02', '2020-01-03')"))
IX = "idx = pd.Index([1, 2, 3])\n"
add("Index.slice_indexer(kind)", IX + SLC.format("idx.slice_indexer(2, 3, kind='loc')"),
    IX + SLC.format("idx.slice_indexer(2, 3)"))
add("Index.get_slice_bound(kind)", IX + "result = idx.get_slice_bound(2, 'left', kind='loc')",
    IX + "result = idx.get_slice_bound(2, 'left')")
add("Index.slice_locs(kind)", IX + "result = idx.slice_locs(2, 3, kind='loc')", IX + "result = idx.slice_locs(2, 3)")
add("MultiIndex.get_slice_bound(kind)", MI + "result = mi.get_slice_bound(('b', 2), 'left', kind='loc')",
    MI + "result = mi.get_slice_bound(('b', 2), 'left')")
add("MultiIndex.slice_locs(kind)", MI + "result = mi.slice_locs(('a', 1), ('b', 2), kind='loc')",
    MI + "result = mi.slice_locs(('a', 1), ('b', 2))")

add("Index.copy(names)", "idx = pd.Index([1, 2])\nresult = idx.copy(names=['x']).name",
    "idx = pd.Index([1, 2])\nresult = idx.copy(name='x').name")
add("RangeIndex.copy(names)", "idx = pd.RangeIndex(2)\nresult = idx.copy(names=['x']).name",
    "idx = pd.RangeIndex(2)\nresult = idx.copy(name='x').name")
add("RangeIndex.copy(dtype)", "idx = pd.RangeIndex(2)\nc = idx.copy(dtype='float64')\nresult = (list(c), str(c.dtype))",
    "idx = pd.RangeIndex(2)\nc = idx.copy().astype('float64')\nresult = (list(c), str(c.dtype))")
add("MultiIndex.copy(dtype)", MI + "c = mi.copy(dtype='object')\nresult = (list(c), str(c.dtype))",
    MI + "c = mi.copy().astype('object')\nresult = (list(c), str(c.dtype))")
add("MultiIndex.copy(codes)", MI + "result = list(mi.copy(codes=[[1, 0], [1, 0]]))",
    MI + "result = list(mi.copy().set_codes([[1, 0], [1, 0]]))")
add("MultiIndex.copy(levels)", MI + "result = list(mi.copy(levels=[['x', 'y'], [1, 2]]))",
    MI + "result = list(mi.copy().set_levels([['x', 'y'], [1, 2]]))")
add("MultiIndex.set_codes(inplace)", MI + "mi.set_codes([[1, 0], [1, 0]], inplace=True)\nresult = list(mi)",
    MI + "mi = mi.set_codes([[1, 0], [1, 0]])\nresult = list(mi)")
add("MultiIndex.set_levels(inplace)", MI + "mi.set_levels([['x', 'y'], [1, 2]], inplace=True)\nresult = list(mi)",
    MI + "mi = mi.set_levels([['x', 'y'], [1, 2]])\nresult = list(mi)")
add("NDArrayBackedExtensionArray.shift(axis)", ARR + "result = arr.shift(1, axis=0)", ARR + "result = arr.shift(1)")
add("NDFrame.between_time(include_start)", S_H + "result = s.between_time('01:00', '03:00', include_start=False)",
    S_H + "result = s.between_time('01:00', '03:00', inclusive='right')", "full")
add("NDFrame.take(is_copy)", DF + "result = df.take([2, 0], is_copy=False)", DF + "result = df.take([2, 0])")
add("Series.take(is_copy)", S3 + "result = s.take([2, 0], is_copy=False)", S3 + "result = s.take([2, 0])", "full")
PI = "pi = pd.period_range('2020-01', periods=2, freq='M')\n"
add("PeriodIndex.astype(how)", PI + "result = pi.astype('datetime64[ns]', how='end')",
    PI + "result = pi.to_timestamp(how='end')")
add("Series.groupby(squeeze)", S3 + "result = s.groupby([1, 1, 2], squeeze=True).sum()",
    S3 + "result = s.groupby([1, 1, 2]).sum()", "full")
add("Series.set_axis(inplace)", S3 + "s.set_axis(['a', 'b', 'c'], inplace=True)\nresult = s",
    S3 + "s = s.set_axis(['a', 'b', 'c'])\nresult = s", "full")
add("pandas.bdate_range(closed)", "result = pd.bdate_range('2020-01-06', '2020-01-10', closed='left')",
    "result = pd.bdate_range('2020-01-06', '2020-01-10', inclusive='left')")
add("pandas.eval(truediv)", "result = pd.eval('7 / 2', truediv=True)", "result = pd.eval('7 / 2')")
add("pandas.infer_freq(warn)", DTI + "result = pd.infer_freq(idx, warn=False)", DTI + "result = pd.infer_freq(idx)")
LR = ("data = pd.DataFrame({'hr1': [514, 573], 'hr2': [545, 526], 'team': ['Red', 'Blue'], 'year1': [2007, 2007], "
      "'year2': [2008, 2008]})\ngroups = {'year': ['year1', 'year2'], 'hr': ['hr1', 'hr2']}\n")
add("pandas.lreshape(label)", LR + "result = pd.lreshape(data, groups, label='x')", LR + "result = pd.lreshape(data, groups)")
add("pandas.read_csv(mangle_dupe_cols)", "result = pd.read_csv(io.StringIO('a,a\\n1,2\\n'), mangle_dupe_cols=True)",
    "result = pd.read_csv(io.StringIO('a,a\\n1,2\\n'))")
add("pandas.read_table(mangle_dupe_cols)", "result = pd.read_table(io.StringIO('a\\ta\\n1\\t2\\n'), mangle_dupe_cols=True)",
    "result = pd.read_table(io.StringIO('a\\ta\\n1\\t2\\n'))")
BAD = "io.StringIO('a,b\\n1,2\\n3,4,5\\n6,7\\n')"
BAD_T = "io.StringIO('a\\tb\\n1\\t2\\n3\\t4\\t5\\n6\\t7\\n')"
add("pandas.read_csv(warn_bad_lines)", f"result = pd.read_csv({BAD}, error_bad_lines=False, warn_bad_lines=False)",
    f"result = pd.read_csv({BAD}, on_bad_lines='skip')")
add("pandas.read_table(warn_bad_lines)", f"result = pd.read_table({BAD_T}, error_bad_lines=False, warn_bad_lines=False)",
    f"result = pd.read_table({BAD_T}, on_bad_lines='skip')")
add("pandas.read_table(error_bad_lines)", f"result = pd.read_table({BAD_T}, error_bad_lines=False)",
    f"result = pd.read_table({BAD_T}, on_bad_lines='skip')")
add("pandas.read_table(prefix)", "result = pd.read_table(io.StringIO('1\\t2\\n3\\t4\\n'), header=None, prefix='c')",
    "result = pd.read_table(io.StringIO('1\\t2\\n3\\t4\\n'), header=None).add_prefix('c')")
add("pandas.read_table(squeeze)", "result = pd.read_table(io.StringIO('x\\n1\\n2\\n'), squeeze=True)",
    "result = pd.read_table(io.StringIO('x\\n1\\n2\\n')).squeeze('columns')")
add("pandas.arrays.SparseArray(index)", "result = list(pd.arrays.SparseArray(1, index=[0, 1, 2]))",
    "result = list(pd.arrays.SparseArray(np.full(3, 1)))")
for f, objs in [("assert_frame_equal", "pd.DataFrame({'a': [1.0]}), pd.DataFrame({'a': [1.0001]})"),
                ("assert_series_equal", "pd.Series([1.0]), pd.Series([1.0001])"),
                ("assert_index_equal", "pd.Index([1.0]), pd.Index([1.0001]), check_exact=False"),
                ("assert_extension_array_equal", "pd.array([1.0], dtype='Float64'), pd.array([1.0001], dtype='Float64')")]:
    add(f"pandas.testing.{f}(check_less_precise)",
        f"pd.testing.{f}({objs}, check_less_precise=True)\nresult = 'equal'",
        f"pd.testing.{f}({objs})\nresult = 'equal'")

# ---------------- NumPy ----------------
add("generic.itemset", "x = np.float64(1.0)\nx.itemset(2.0)\nresult = x", None)
add("ndarray.itemset", "a = np.zeros(3)\na.itemset(1, 5.0)\nresult = a", "a = np.zeros(3)\na[1] = 5.0\nresult = a")
add("generic.newbyteorder", "x = np.int16(1)\nresult = int(x.newbyteorder('>'))",
    "x = np.int16(1)\nresult = int(x.view(x.dtype.newbyteorder('>')))")
add("generic.ptp", "result = np.float64(3.0).ptp()", "result = np.ptp(np.float64(3.0))")
for n in ("ComplexWarning", "ModuleDeprecationWarning", "RankWarning", "TooHardError"):
    add(f"numpy.{n}", f"result = np.{n}.__name__", f"result = np.exceptions.{n}.__name__")
add("numpy.DataSource", "result = np.DataSource.__name__", "result = np.lib.npyio.DataSource.__name__")
add("numpy.Infinity", "result = np.Infinity", "result = np.inf")
add("numpy.NZERO", "result = str(np.NZERO)", "result = str(-0.0)")
add("numpy.PINF", "result = np.PINF", "result = np.inf")
add("numpy.PZERO", "result = str(np.PZERO)", "result = str(0.0)")
add("numpy.clongfloat", "result = np.clongfloat", "result = np.clongdouble")
add("numpy.longcomplex", "result = np.longcomplex", "result = np.clongdouble")
add("numpy.singlecomplex", "result = np.singlecomplex", "result = np.complex64")
add("numpy.complex", "result = np.complex", "result = complex")
add("numpy.unicode", "result = np.unicode", "result = str")
add("numpy.format_parser", "result = str(np.format_parser(['i4', 'f8'], ['a', 'b'], []).dtype)",
    "result = str(np.rec.format_parser(['i4', 'f8'], ['a', 'b'], []).dtype)")
add("numpy.issctype", "result = [np.issctype(t) for t in (np.float64, int)]",
    "result = [issubclass(t, np.generic) for t in (np.float64, int)]")
add("numpy.msort", "result = np.msort(np.array([[3, 1], [2, 4]]))", "result = np.sort(np.array([[3, 1], [2, 4]]), axis=0)")
SRC = ("import os, sys, tempfile, importlib.util, inspect\n"
       "d = tempfile.mkdtemp()\npath = os.path.join(d, 'mod.py')\n"
       "open(path, 'w').write('def f(x):\\n    return x + 1\\n')\n"
       "spec = importlib.util.spec_from_file_location('mod', path)\nmod = importlib.util.module_from_spec(spec)\n"
       "spec.loader.exec_module(mod)\nbuf = io.StringIO()\n")
add("numpy.source", SRC + "np.source(mod.f, output=buf)\nresult = buf.getvalue().split('\\n\\n', 1)[1]",
    SRC + "print(inspect.getsource(mod.f), file=buf)\nresult = buf.getvalue()")
add("numpy.tracemalloc_domain", "result = np.tracemalloc_domain", "result = np.lib.tracemalloc_domain")
add("numpy.typeDict", "result = np.typeDict['float64']", "result = np.sctypeDict['float64']")
add("numpy.histogram2d(normed)", "result = np.histogram2d([1, 2, 3], [1, 2, 3], bins=2, normed=True)[0]",
    "result = np.histogram2d([1, 2, 3], [1, 2, 3], bins=2, density=True)[0]")
add("numpy.histogramdd(normed)", "result = np.histogramdd([[1, 2, 3]], bins=2, normed=True)[0]",
    "result = np.histogramdd([[1, 2, 3]], bins=2, density=True)[0]")

# ---------------- release-note entries ----------------
R = "pandas-2.0.0-L"
add(R + "733", "result = str(pd.Timestamp('2020-01-01', None, 'UTC'))", "result = str(pd.Timestamp('2020-01-01', tz='UTC'))")
DTS = "s = pd.Series(pd.date_range('2020-01-01', periods=2))\n"
DTX = "idx = pd.DatetimeIndex(['2020-01-01'])\n"
add(R + "739", DTX + "result = idx.astype('int32')", DTX + "result = idx.astype('int64', copy=False).astype('int32')")
add(R + "755", "s = pd.Series(['x', 'y'], dtype='datetime64[ns]')\nresult = (list(s), str(s.dtype))",
    "s = pd.Series(['x', 'y'])\nresult = (list(s), str(s.dtype))")
add(R + "875", "s = pd.Series(pd.Timestamp('2020-01-01 12:00', tz='Asia/Seoul'), index=[0], dtype='datetime64[ns]')\n"
    "result = list(s)",
    "s = pd.Series(pd.Series(pd.Timestamp('2020-01-01 12:00', tz='Asia/Seoul'), index=[0]).dt.tz_localize(None))\n"
    "result = list(s)")
add(R + "876", "s = pd.Series([pd.Timestamp('2020-01-01 12:00', tz='Asia/Seoul')], dtype='datetime64[ns]')\n"
    "result = list(s)",
    "s = pd.Series([pd.Timestamp('2020-01-01 12:00', tz='Asia/Seoul')]).dt.tz_localize(None)\nresult = list(s)")
MR = "data = np.ma.mrecords.fromarrays([[1, 2], [3.0, 4.0]], names='a,b')\n"
add(R + "877", "import numpy.ma.mrecords\n" + MR + "result = pd.DataFrame(data)",
    "import numpy.ma.mrecords\n" + MR + "result = pd.DataFrame({name: data[name] for name in data.dtype.names})")
add(R + "878", "s = pd.Series(['2020-01-01'])\nresult = s.astype('datetime64')", None)
add(R + "879", DTS + "result = s.astype('datetime64[ns, UTC]')", DTS + "result = s.dt.tz_localize('UTC')")
UTC = "s = pd.Series(pd.date_range('2020-01-01', periods=2, tz='UTC'))\n"
add(R + "880", UTC + "result = s.astype('datetime64[ns]')", UTC + "result = s.dt.tz_localize(None)")
add(R + "887", OFF + "result = off(ts)", OFF + "result = off + ts")
add(R + "894", MI + "result = list(mi.set_levels(['x', 'y'], 0))", MI + "result = list(mi.set_levels(['x', 'y'], level=0))")
add(R + "899", "result = pd.Period('2020-01', freq='M').to_timestamp(tz='UTC')",
    "result = pd.Period('2020-01', freq='M').to_timestamp().tz_localize('UTC')")
add(R + "906", MI_DF + "result = df.xs(['a', 1])", MI_DF + "result = df.xs(('a', 1))")
add(R + "907", "result = pd.Index(['2020-01-01', '2020-01-02'], tz='UTC')",
    "result = pd.DatetimeIndex(['2020-01-01', '2020-01-02'], tz='UTC')")
POS = {
    914: (DF + "result = df.drop('a', 1)", DF + "result = df.drop('a', axis=1)"),
    915: ("s = pd.Series([1.0, None])\nresult = s.fillna(0, None)", "s = pd.Series([1.0, None])\nresult = s.fillna(0)"),
    916: ("s = pd.Series(['a-b-c'])\nresult = s.str.split('-', 1)", "s = pd.Series(['a-b-c'])\nresult = s.str.split('-', n=1)"),
    917: (DF + "result = df.set_index('a', False)", DF + "result = df.set_index('a', drop=False)"),
    918: (S_H + "result = s.resample('30min').interpolate('linear', 0)",
          S_H + "result = s.resample('30min').interpolate('linear', axis=0)"),
    919: (DF + "result = df.reset_index(None, True)", DF + "result = df.reset_index(drop=True)"),
    920: ("df = pd.DataFrame({'a': [1, None]})\nresult = df.dropna(0)",
          "df = pd.DataFrame({'a': [1, None]})\nresult = df.dropna(axis=0)"),
    921: ("result = pd.array([3, 1, 2], dtype='Int64').argsort(False)",
          "result = pd.array([3, 1, 2], dtype='Int64').argsort(ascending=False)"),
    922: ("result = pd.Categorical(['a', 'b']).sort_values(False, False)",
          "result = pd.Categorical(['a', 'b']).sort_values(inplace=False, ascending=False)"),
    923: ("result = pd.Index([1, 1, 2]).drop_duplicates('last')", "result = pd.Index([1, 1, 2]).drop_duplicates(keep='last')"),
    924: ("df = pd.DataFrame({'a': [1, 1], 'b': [2, 3]})\nresult = df.drop_duplicates('a', 'last')",
          "df = pd.DataFrame({'a': [1, 1], 'b': [2, 3]})\nresult = df.drop_duplicates('a', keep='last')"),
    925: ("df = pd.DataFrame({'a': [1, 2]}, index=[1, 0])\nresult = df.sort_index(0)",
          "df = pd.DataFrame({'a': [1, 2]}, index=[1, 0])\nresult = df.sort_index(axis=0)"),
    926: ("df = pd.DataFrame({'a': [1.0, None, 3.0]})\nresult = df.interpolate('linear', 0)",
          "df = pd.DataFrame({'a': [1.0, None, 3.0]})\nresult = df.interpolate('linear', axis=0)"),
    927: (DF + "result = df.any(0)", DF + "result = df.any(axis=0)"),
    928: ("result = pd.Index([1, 2]).set_names('x', None)", "result = pd.Index([1, 2]).set_names('x', level=None)"),
    929: ("result = pd.Index([1, 2]).join(pd.Index([2, 3]), 'inner')",
          "result = pd.Index([1, 2]).join(pd.Index([2, 3]), how='inner')"),
    930: (S3 + "result = pd.concat([s, s], 1)", S3 + "result = pd.concat([s, s], axis=1)"),
    931: ("df = pd.DataFrame({'a': [1, 2], 'b': ['x', 'y'], 'c': [3, 4]})\nresult = pd.pivot(df, 'a', 'b', 'c')",
          "df = pd.DataFrame({'a': [1, 2], 'b': ['x', 'y'], 'c': [3, 4]})\n"
          "result = pd.pivot(df, index='a', columns='b', values='c')"),
    932: ("df = pd.DataFrame({'a': [1, 2], 'b': ['x', 'y'], 'c': [3, 4]})\nresult = df.pivot('a', 'b', 'c')",
          "df = pd.DataFrame({'a': [1, 2], 'b': ['x', 'y'], 'c': [3, 4]})\n"
          "result = df.pivot(index='a', columns='b', values='c')"),
    934: ("result = pd.read_json(io.StringIO('[{\"a\": 1}]'), 'records')",
          "result = pd.read_json(io.StringIO('[{\"a\": 1}]'), orient='records')"),
    936: (DF + "buf = io.BytesIO()\ndf.to_stata(buf, write_index=False)\nbuf.seek(0)\nresult = pd.read_stata(buf, False)",
          DF + "buf = io.BytesIO()\ndf.to_stata(buf, write_index=False)\nbuf.seek(0)\n"
          "result = pd.read_stata(buf, convert_dates=False)"),
    937: ("result = pd.read_csv(io.StringIO('a;b\\n1;2\\n'), ';')", "result = pd.read_csv(io.StringIO('a;b\\n1;2\\n'), sep=';')"),
    938: ("result = pd.read_table(io.StringIO('a,b\\n1,2\\n'), ',')",
          "result = pd.read_table(io.StringIO('a,b\\n1,2\\n'), sep=',')"),
    939: ("result = pd.read_fwf(io.StringIO('a  b\\n1  2\\n'), [(0, 1), (3, 4)])",
          "result = pd.read_fwf(io.StringIO('a  b\\n1  2\\n'), colspecs=[(0, 1), (3, 4)])"),
    941: (S3 + "result = s.mask(s > 1, 0, False)", S3 + "result = s.mask(s > 1, 0, inplace=False)"),
    942: (DF + "buf = io.BytesIO()\ndf.to_stata(buf, None, False)\nbuf.seek(0)\nresult = pd.read_stata(buf)",
          DF + "buf = io.BytesIO()\ndf.to_stata(buf, convert_dates=None, write_index=False)\nbuf.seek(0)\n"
          "result = pd.read_stata(buf)"),
    943: (S3 + "result = s.where(s > 1, 0, False)", S3 + "result = s.where(s > 1, 0, inplace=False)"),
    944: (S3 + "result = s.set_axis(['a', 'b', 'c'], 0)", S3 + "result = s.set_axis(['a', 'b', 'c'], axis=0)"),
    945: (S3 + "result = s.rename_axis('x', False).index.name", S3 + "result = s.rename_axis('x', inplace=False).index.name"),
    946: (S3 + "result = s.clip(1.5, 2.5, 0)", S3 + "result = s.clip(1.5, 2.5, axis=0)"),
    947: ("s = pd.Series([None, 1.0])\nresult = s.bfill(0)", "s = pd.Series([None, 1.0])\nresult = s.bfill(axis=0)"),
    948: (S3 + "result = s.replace(1.0, 9.0, False)", S3 + "result = s.replace(1.0, 9.0, inplace=False)"),
    949: (DF + "result = df.sort_values('a', 0, False)", DF + "result = df.sort_values('a', axis=0, ascending=False)"),
    950: (S3 + "result = s.sort_values(0, False)", S3 + "result = s.sort_values(axis=0, ascending=False)"),
    951: (DF + "result = df.reindex([1, 0], ['b', 'a'])", DF + "result = df.reindex(index=[1, 0], columns=['b', 'a'])"),
}
for line, (code, alt) in POS.items():
    add(f"{R}{line}", code, alt, "full")
add(R + "953", "result = list(pd.Categorical('a'))", "result = list(pd.Categorical(['a']))")
add(R + "954", "ci = pd.CategoricalIndex(categories=['a', 'b'])\nresult = (list(ci), list(ci.categories))",
    "ci = pd.CategoricalIndex([], categories=['a', 'b'])\nresult = (list(ci), list(ci.categories))")
add(R + "962", "result = pd.Categorical(['a', 'b'], ordered=True).min(numeric_only=True)",
    "result = pd.Categorical(['a', 'b'], ordered=True).min(skipna=True)")
add(R + "970", DF + "result = df.to_dict('r')", DF + "result = df.to_dict('records')")
add(R + "985", DTS + "result = s.shift(1, fill_value=0)", DTS + "result = s.shift(1, fill_value=pd.Timestamp(0))")
TM = "df = pd.DataFrame({'t': pd.date_range('2020-01-01', periods=3), 'x': [1.0, 2.0, 3.0]})\n"
add(R + "986", TM + "result = df.ewm(halflife='1 day', times='t').mean()",
    TM + "result = df[['x']].ewm(halflife='1 day', times=df['t']).mean()")
add(R + "987", S3 + "result = s.between(1.0, 2.0, inclusive=True)", S3 + "result = s.between(1.0, 2.0, inclusive='both')",
    "full")
add(R + "988", "result = pd.read_csv(io.StringIO('a,b\\n1,2\\n'), usecols=[0, 5])",
    "result = pd.read_csv(io.StringIO('a,b\\n1,2\\n'), usecols=[0])")
G3 = "df = pd.DataFrame({'k': [1, 1], 'b': [2, 3], 'c': [4, 5]})\n"
add(R + "990", G3 + "result = df.groupby('k')['b', 'c'].sum()", G3 + "result = df.groupby('k')[['b', 'c']].sum()")
add(R + "991", MI_S + "result = s.loc[(slice(None), [1, 3])]", MI_S + "result = s[s.index.isin([1, 3], level=1)]", "full")
LS = "s = pd.Series([1, 2, 3], index=['a', 'b', 'c'])\n"
add(R + "992", LS + "s.loc[0:2] = 9\nresult = s", LS + "s.iloc[0:2] = 9\nresult = s", "full")
add(R + "993", LS + "result = s[1.0]", LS + "result = s.iloc[1]")
add(R + "994", DF + "result = df.iloc[pd.DataFrame({'a': [True, False, True], 'b': [True, False, True]})]", None)
add(R + "995", LS + "result = s[{'a'}]", LS + "result = s[['a']]")
add(R + "996", S3 + "result = s[:, None]", S3 + "result = s.to_numpy()[:, None]")
MG = "l = pd.DataFrame({'k': [1], 'v': [2]})\nr = pd.DataFrame({'k': [1], 'v': [3]})\n"
add(R + "997", MG + "result = pd.merge(l, r, on='k', suffixes={'_l': 0, '_r': 0})",
    MG + "result = pd.merge(l, r, on='k', suffixes=('_l', '_r'))")
add(R + "1003", CAT + "cat.categories = ['x', 'y']\nresult = list(cat)",
    CAT + "cat = cat.rename_categories(['x', 'y'])\nresult = list(cat)")
add(R + "1006", DF + "buf = io.BytesIO()\ndf.to_stata(fname=buf, write_index=False)\nbuf.seek(0)\nresult = pd.read_stata(buf)",
    DF + "buf = io.BytesIO()\ndf.to_stata(path=buf, write_index=False)\nbuf.seek(0)\nresult = pd.read_stata(buf)")
add(R + "1007", S3 + "result = s[[slice(0, 2)]]", S3 + "result = s[slice(0, 2)]", "full")
DFD = "df = pd.DataFrame({'v': [1, 2]}, index=pd.to_datetime(['2020-01-01', '2020-01-02']))\n"
add(R + "1008", DFD + "result = df['2020-01']", DFD + "result = df.loc['2020-01']")
LONG = "df = pd.DataFrame({'a': ['x' * 60]})\n"
add(R + "1009", LONG + "pd.set_option('display.max_colwidth', -1)\nresult = repr(df)",
    LONG + "pd.set_option('display.max_colwidth', None)\nresult = repr(df)")
add(R + "1010", DF + "pd.set_option('display.column_space', 20)\nresult = (df.to_string(), repr(df))",
    DF + "result = (df.to_string(), repr(df))")
IA = "a = pd.Index(['a', 'b'])\nb = pd.Index(['b', 'c'])\n"
add(R + "1024", IA + "result = [list(a & b), list(a | b), list(a ^ b)]",
    IA + "result = [list(a.intersection(b)), list(a.union(b)), list(a.symmetric_difference(b))]")
add(R + "1026", "df = pd.DataFrame({'a': ['x']}, dtype='float64')\nresult = (df['a'].tolist(), str(df['a'].dtype))",
    "df = pd.DataFrame({'a': ['x']})\nresult = (df['a'].tolist(), str(df['a'].dtype))")
add(R + "1033", "s = pd.Series([1.0, np.nan], dtype='int64')\nresult = (s.tolist(), str(s.dtype))",
    "s = pd.Series([1.0, np.nan])\nresult = (s.tolist(), str(s.dtype))")
add(R + "1034", "s = pd.Series([300], dtype='int8')\nresult = (s.tolist(), str(s.dtype))",
    "s = pd.Series([300]).astype('int8')\nresult = (s.tolist(), str(s.dtype))")
DT64 = "values = np.array(['2020-01-01'], dtype='datetime64[ns]')\n"
add(R + "1035", DT64 + "result = pd.Series(values, dtype='int64')", DT64 + "result = pd.Series(values.view('int64'))")
add(R + "1041", "result = pd.Timestamp('2020-01-01') < datetime.date(2020, 1, 2)",
    "result = pd.Timestamp('2020-01-01') < pd.Timestamp(datetime.date(2020, 1, 2))")
add(R + "1042", "result = pd.NaT < datetime.date(2020, 1, 2)", "result = pd.NaT < pd.Timestamp(datetime.date(2020, 1, 2))")
add(R + "1048", "s = pd.Series([1, 3], dtype='category')\nresult = s.diff()",
    "s = pd.Series([1, 3], dtype='category')\nresult = s.astype('int64').diff()")
add(R + "1049", "df = pd.DataFrame({'a': [1, 2]})\nresult = np.add.outer(df, df)",
    "df = pd.DataFrame({'a': [1, 2]})\nresult = np.add.outer(df.to_numpy(), df.to_numpy())")
add(R + "1050", "result = pd.Series(['a', 'b']).rank(numeric_only=True)", None)
AL = "left = pd.DataFrame({'a': [1], 'b': [2]})\nright = pd.Series([2, 3], index=['b', 'c'])\n"
add(R + "1052", AL + "result = left == right",
    AL + "left, right = left.align(right, axis=1, copy=False)\nresult = left == right")
NUM = "df = pd.DataFrame({'k': [1, 1], 'v': [1.0, 3.0], 't': ['x', 'y']})\n"
add(R + "1053", NUM + "result = df.mean()", NUM + "result = df.mean(numeric_only=True)", "full")
NUMT = ("df = pd.DataFrame({'v': [1.0, 3.0], 't': ['x', 'y']}, "
        "index=pd.date_range('2020-01-01', periods=2, freq='H'))\n")
add(R + "1056", NUMT + "result = df.resample('D').mean()", NUMT + "result = df.resample('D').mean(numeric_only=True)")
add(R + "1057", NUM + "result = df[['v', 't']].rolling(2).sum()", NUM + "result = df[['v', 't']].rolling(2).sum(numeric_only=True)")
add(R + "1059", NUM + "result = df.groupby('k').std()", NUM + "result = df.groupby('k').std(numeric_only=True)")
add(R + "1060", NUMT + "result = df.resample('D').median()", NUMT + "result = df.resample('D').median(numeric_only=True)")
add(R + "1065", S3 + "result = s.rolling(2).sum(foo=1)", S3 + "result = s.rolling(2).sum()", "full")
add(R + "1068", DF + "result = df.eval('a + 1', False)", DF + "result = df.eval('a + 1', inplace=False)", "full")

N = "numpy-"
add(N + "1.24.0-L89", "result = np.array([[1, 2], [3]]).tolist()", "result = np.array([[1, 2], [3]], dtype=object).tolist()")
add(N + "1.24.0-L113", "result = np.add(np.arange(3), 1, dtype=np.dtype('>i8'))",
    "result = np.add(np.arange(3), 1, dtype='int64')")
add(N + "1.25.0-L119", "result = np.stack(x for x in [np.zeros(2), np.ones(2)])",
    "result = np.stack([x for x in [np.zeros(2), np.ones(2)]])")
add(N + "1.25.0-L124", "out = np.empty(3, dtype=int)\nresult = np.clip(np.arange(3), 0.5, 1.5, out=out)",
    "out = np.empty(3, dtype=int)\nresult = np.clip(np.arange(3), 0.5, 1.5, out=out, casting='unsafe')")
add(N + "1.25.0-L206", "out = np.empty(1)\nnp.fix(np.array([1.5]), y=out)\nresult = out",
    "out = np.empty(1)\nnp.fix(np.array([1.5]), out=out)\nresult = out")
LT = "conv = {0: lambda b: float(b.decode())}\n"
add(N + "2.0.0-L410", LT + "result = np.loadtxt(io.StringIO('1\\n2\\n'), converters=conv)",
    LT + "result = np.loadtxt(io.StringIO('1\\n2\\n'), converters=conv, encoding='bytes')")
SV = "a = np.stack([np.eye(2)] * 3)\nb = np.ones((3, 2))\n"
add(N + "2.0.0-L454", SV + "result = np.linalg.solve(a, b)", SV + "result = np.linalg.solve(a, b[..., None])[..., 0]")
add(N + "2.0.0-L1407", "result = np.concatenate([np.zeros(2), np.ones(2)], axis=32)",
    "result = np.concatenate([np.zeros(2), np.ones(2)], axis=None)")
add(N + "2.0.0-L1420", "result = np.array(np.arange(3), dtype=float, copy=False)",
    "result = np.asarray(np.arange(3), dtype=float)")
add(N + "2.1.0-L52", "result = [a.tolist() for a in np.nonzero(np.int64(5))]",
    "result = [a.tolist() for a in np.atleast_1d(np.int64(5)).nonzero()]")
add(N + "2.1.0-L340", "a = np.zeros(2, dtype='int8')\nnp.copyto(a, 1000)\nresult = a",
    "a = np.zeros(2, dtype='int8')\nnp.copyto(a, np.array(1000))\nresult = a")
add("Rolling.quantile(quantile)", S3 + "result = s.rolling(2).quantile(quantile=0.5)",
    S3 + "result = s.rolling(2).quantile(q=0.5)", "full")
add("Expanding.quantile(quantile)", S3 + "result = s.expanding().quantile(quantile=0.5)",
    S3 + "result = s.expanding().quantile(q=0.5)", "full")

# Rows that cannot be run, with the reason
NOT_RUN = {R + "935": "the old code needs a SAS file, which pandas cannot write"}
