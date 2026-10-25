"""List the public API of pandas or NumPy as installed in the running environment.

Run it with the Python of the environment to inspect, for example
    measurements/envs/old/bin/python screening/api_dump.py pandas screening/results/pandas_old.json

Scope: the namespaces each library documents for general use.
  pandas  the public API as the pandas API reference defines it: pandas.* and the public
          subpackages (PANDAS_MODULES), and from pandas.io and pandas.tseries only the names the
          reference documents (PANDAS_DOCUMENTED)
  NumPy   the main namespaces listed in "NumPy's module structure" that exist in NumPy 1.23.5
          (NUMPY_MODULES)
Members are listed for each of these modules, for every class of the library that they expose,
for the singletons pd.NaT and pd.NA, and for the objects returned by the .dt/.str/.cat accessors
and by groupby, resample, rolling, expanding and ewm.

A member is public if its name does not start with an underscore. Names that a module serves through
its module-level __getattr__ are added as well (for example np.float in NumPy 1.23.5 or pd.np in
pandas 1.5.3), because dir() does not list them. They are kept only if they can be accessed and are
not placeholders that exist only to raise an error (such as NumPy's expired financial functions or
the empty SparseDataFrame class of pandas 1.5.3).

For classes, each member is also accessed on a sample object (for example a real array, not only
the ndarray class), because some removed members remain on the class and fail only on use, as
ndarray.ptp does in NumPy 2.x; such members count as not accessible.

For each member the listing records its kind, the class that defines it (for members of classes),
and, for callables, its parameter names. With --probe OTHER.json, it also records which members of
OTHER.json are not listed here but can still be accessed, so that a hidden name is not mistaken for
a removed one.
"""
import argparse
import inspect
import json
import re
import sys
import warnings

warnings.simplefilter("ignore")

HIDDEN_DICTS = ("__deprecated_attrs__", "__expired_functions__", "__former_attrs__",
                "__future_scalars__", "__expired_attributes__")

# pandas: the public API as the pandas API reference defines it: pandas.* and the public
# subpackages; pandas.core, pandas.compat and pandas.util are private.
PANDAS_MODULES = ["pandas", "pandas.api.types", "pandas.api.extensions", "pandas.api.indexers",
                  "pandas.api.interchange", "pandas.arrays", "pandas.errors", "pandas.plotting",
                  "pandas.testing", "pandas.tseries.offsets"]
# From pandas.io and pandas.tseries, only the names the API reference documents. pandas.io.formats.style
# (Styler) is documented too, but importing it needs jinja2, an extra package (criterion 4).
PANDAS_DOCUMENTED = {"pandas.io.json": ["build_table_schema"],
                     "pandas.io.stata": ["StataReader", "StataWriter"],
                     "pandas.tseries.frequencies": ["to_offset"]}
# NumPy: the main namespaces of "NumPy's module structure" that exist in NumPy 1.23.5. The
# special-purpose (numpy.lib, numpy.rec, ...) and legacy (numpy.ma, numpy.matlib, ...) namespaces
# are not included.
NUMPY_MODULES = ["numpy", "numpy.fft", "numpy.linalg", "numpy.polynomial", "numpy.polynomial.chebyshev",
                 "numpy.polynomial.hermite", "numpy.polynomial.hermite_e", "numpy.polynomial.laguerre",
                 "numpy.polynomial.legendre", "numpy.polynomial.polynomial", "numpy.random", "numpy.testing",
                 "numpy.typing"]


def module_targets(library):
    """{module name: (module, names to list or None for all)} for the modules in scope."""
    import importlib
    spec = PANDAS_MODULES if library == "pandas" else NUMPY_MODULES
    out = {}
    for name in spec:
        out[name] = (importlib.import_module(name), None)
    if library == "pandas":
        for name, names in PANDAS_DOCUMENTED.items():
            out[name] = (importlib.import_module(name), names)
    return out


def class_targets(library, modules, known):
    """{name: (class, sample)} for every class of the library that a module in scope exposes.

    A class is listed once, under the first public name it is found at; names that a module lists
    are searched before hidden names, so that a deprecated alias does not become the name. Within a
    module, names without digits come first, so that a NumPy scalar type is named by its C name
    (longdouble), which every platform has, not by a size alias (float128), which some lack. Classes
    already in `known` (inspected with a sample object) are skipped.
    """
    seen = {id(cls) for cls, _ in known.values()}
    found = []
    for hidden_pass in (False, True):
        for mname, (module, only) in modules.items():
            if only:
                names = set() if hidden_pass else set(only)
            else:
                listed = {n for n in dir(module) if not n.startswith("_")}
                names = hidden_names(module) - listed if hidden_pass else listed
            for n in sorted(names, key=lambda x: (any(c.isdigit() for c in x), x)):
                try:
                    value = getattr(module, n)
                except Exception:  # noqa: BLE001 - not accessible
                    continue
                if not inspect.isclass(value) or id(value) in seen:
                    continue
                if not (getattr(value, "__module__", "") or "").startswith(library):
                    continue  # e.g. np.float in NumPy 1.23.5 is the built-in float
                seen.add(id(value))
                found.append((f"{mname}.{n}", value))
    return {name: (cls, sample_of(library, cls)) for name, cls in found}


def sample_of(library, cls):
    """A sample object for classes whose removed members may stay on the class (see the docstring)."""
    if library != "numpy":
        return None
    import numpy as np
    try:
        if issubclass(cls, np.generic):
            return cls(0)
        return {np.finfo: lambda: np.finfo(np.float64), np.iinfo: lambda: np.iinfo(np.int64),
                np.dtype: lambda: np.dtype("float64")}.get(cls, lambda: None)()
    except Exception:  # noqa: BLE001 - abstract scalar types cannot be created
        return None


def targets(library):
    """{name: (inspected object, sample object or None)}"""
    known = sampled_targets(library)
    modules = module_targets(library)
    out = {name: (module, None) for name, (module, _) in modules.items()}
    out.update(known)
    out.update(class_targets(library, modules, known))
    return out


def documented_only(library):
    """{module name: names} for modules of which only some names are listed."""
    return {name: names for name, (_, names) in module_targets(library).items() if names}


def sampled_targets(library):
    """Classes inspected with a sample object, and the objects returned by methods (such as groupby)."""
    if library == "pandas":
        import pandas as pd
        df = pd.DataFrame({"a": [1, 2], "b": [3.0, 4.0]})
        s = pd.Series([1.0, 2.0, 3.0])
        ts = pd.Series([1, 2, 3], index=pd.date_range("2020-01-01", periods=3))
        samples = {
            "DataFrame": df,
            "Series": s,
            "Index": pd.Index(["x", "y", "z"]),
            "DatetimeIndex": pd.date_range("2020-01-01", periods=3),
            "TimedeltaIndex": pd.timedelta_range("1 day", periods=3),
            "PeriodIndex": pd.period_range("2020-01", periods=3, freq="M"),
            "CategoricalIndex": pd.CategoricalIndex(["a", "b", "a"]),
            "IntervalIndex": pd.interval_range(0, 3),
            "MultiIndex": pd.MultiIndex.from_tuples([(1, "a"), (2, "b")]),
            "RangeIndex": pd.RangeIndex(3),
            "Categorical": pd.Categorical(["a", "b", "a"]),
            "Timestamp": pd.Timestamp("2020-01-01"),
            "Timedelta": pd.Timedelta("1 day"),
            "Period": pd.Period("2020-01", freq="M"),
            "Series.dt": pd.Series(pd.date_range("2020-01-01", periods=3)).dt,
            "Series.str": pd.Series(["a"]).str,
            "Series.cat": pd.Series(["a"], dtype="category").cat,
            "DataFrameGroupBy": df.groupby("a"),
            "SeriesGroupBy": s.groupby([1, 1, 2]),
            "Resampler": ts.resample("D"),
            "Rolling": s.rolling(2),
            "Expanding": s.expanding(),
            "ExponentialMovingWindow": s.ewm(com=1),
            "NaT": pd.NaT,
            "NA": pd.NA,
        }
        classes = {"DataFrame": pd.DataFrame, "Series": pd.Series, "Index": pd.Index,
                   "DatetimeIndex": pd.DatetimeIndex, "TimedeltaIndex": pd.TimedeltaIndex,
                   "PeriodIndex": pd.PeriodIndex, "CategoricalIndex": pd.CategoricalIndex,
                   "IntervalIndex": pd.IntervalIndex, "MultiIndex": pd.MultiIndex, "RangeIndex": pd.RangeIndex,
                   "Categorical": pd.Categorical, "Timestamp": pd.Timestamp, "Timedelta": pd.Timedelta,
                   "Period": pd.Period}
        return {name: (classes.get(name, type(sample)), sample) for name, sample in samples.items()}
    import numpy as np
    return {"ndarray": (np.ndarray, np.arange(3))}


def hidden_names(module):
    """Names that the module serves through its module-level __getattr__."""
    names = set()
    for attr in HIDDEN_DICTS:
        value = module.__dict__.get(attr)
        if isinstance(value, (dict, set, list, tuple, frozenset)):
            names.update(value)
    getattr_fn = module.__dict__.get("__getattr__")
    if getattr_fn is not None:
        try:
            source = inspect.getsource(getattr_fn)
        except (OSError, TypeError):
            source = ""
        names.update(re.findall(r"name == [\"'](\w+)[\"']", source))
        for group in re.findall(r"name in [\{\(\[]([^\}\)\]]*)[\}\)\]]", source):
            names.update(re.findall(r"[\"'](\w+)[\"']", group))
    return {n for n in names if isinstance(n, str) and not n.startswith("_")}


def accessible(obj, name, sample=None):
    """True if the name can be used: on the object, and on the sample object when there is one."""
    try:
        getattr(obj, name)
    except Exception:  # noqa: BLE001 - any failure means the name cannot be used
        return False
    if sample is not None:
        try:
            getattr(sample, name)
        except AttributeError as e:
            # accessors such as .str refuse data of the wrong type; that is not a removal
            if not str(e).startswith("Can only use"):
                return False
        except Exception:  # noqa: BLE001 - exists, but fails for this particular sample
            pass
    return True


def parameters(value):
    """Parameter names of a callable, and whether it also accepts arbitrary keyword arguments."""
    try:
        sig = inspect.signature(value)
    except (TypeError, ValueError):
        return None, None
    names = [p.name for p in sig.parameters.values()
             if p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD) and p.name not in ("self", "cls")]
    var_kw = any(p.kind is p.VAR_KEYWORD for p in sig.parameters.values())
    return names, var_kw


def is_placeholder(value):
    """An object a module returns only to raise a helpful error: a local stub or an empty class."""
    if "<locals>" in getattr(value, "__qualname__", ""):
        return True
    if inspect.isclass(value):
        return set(value.__dict__) <= {"__module__", "__dict__", "__weakref__", "__doc__", "__qualname__"}
    return False


def kind_of(owner_obj, value):
    if inspect.ismodule(value):
        return "module"
    if inspect.isclass(value):
        return "class"
    if callable(value):
        return "function" if inspect.ismodule(owner_obj) else "method"
    return "value" if inspect.ismodule(owner_obj) else "attribute"


def defining_class(cls, name):
    for c in cls.__mro__:
        if name in c.__dict__:
            return c.__name__
    return cls.__name__


def listing(obj, sample):
    listed = {n for n in dir(obj) if not n.startswith("_")}
    hidden = hidden_names(obj) if inspect.ismodule(obj) else set()
    members = {}
    for name in sorted(listed | hidden):
        if not accessible(obj, name, sample):
            continue
        value = getattr(obj, name)
        if name in hidden and name not in listed and is_placeholder(value):
            continue
        member = {"kind": kind_of(obj, value)}
        if name in hidden and name not in listed:
            member["hidden"] = True
        if inspect.isclass(obj):
            member["defined_in"] = defining_class(obj, name)
        if callable(value) and not inspect.ismodule(value):
            params, var_kw = parameters(value)
            if params is not None:
                member["params"] = params
                if var_kw:
                    member["accepts_any_keyword"] = True
        members[name] = member
    return members


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("library", choices=["pandas", "numpy"])
    ap.add_argument("out")
    ap.add_argument("--probe", help="listing from the other version")
    a = ap.parse_args()

    import numpy
    import pandas
    objs = targets(a.library)
    only = documented_only(a.library)
    out = {"library": a.library, "python": sys.version.split()[0],
           "pandas": pandas.__version__, "numpy": numpy.__version__, "targets": {}}
    for tname, (obj, sample) in objs.items():
        members = listing(obj, sample)
        if tname in only:
            members = {k: v for k, v in members.items() if k in only[tname]}
        out["targets"][tname] = {"type_name": obj.__name__, "members": members}
    if a.probe:
        other = json.load(open(a.probe, encoding="utf-8"))
        for tname, entry in out["targets"].items():
            missing = [n for n in other["targets"].get(tname, {}).get("members", {}) if n not in entry["members"]]
            if tname in only:
                missing = [n for n in missing if n in only[tname]]
            entry["still_accessible"] = sorted(n for n in missing if accessible(*objs[tname], n))
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    n = sum(len(e["members"]) for e in out["targets"].values())
    print(f"{a.library} {out[a.library]} (Python {out['python']}): {len(objs)} objects, {n} public members -> {a.out}")


if __name__ == "__main__":
    main()
