"""Record what the old version says about each removed name or parameter (criterion 3).

Run it with the Python of the old environment of the library, for example
    measurements/envs/old/bin/python screening/deprecation_messages.py pandas
    measurements/envs/mid/bin/python screening/deprecation_messages.py numpy
Reads results/<library>_api_diff.csv and writes results/<library>_deprecations.csv.

For each row of the API comparison, three sources in the old version are recorded:
  warning    the warnings raised when the name is accessed on the inspected object (and on its sample
             object), for example the deprecation warning of np.float
  source     the messages of warnings.warn(...) calls in the source code of the member, or, for a
             removed parameter, those that mention the parameter
  docstring  the ".. deprecated::" notes and, for a removed parameter, its description in the docstring
These are pointers for reading; whether a replacement is documented is decided by reading them
together with the release notes.
"""
import csv
import inspect
import os
import re
import sys
import warnings

from api_dump import targets

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")


def warns_on_access(obj, name, sample):
    out = []
    for target in (obj, sample):
        if target is None:
            continue
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                getattr(target, name)
            except Exception:  # noqa: BLE001 - the access itself is not what is recorded
                pass
        out += [str(w.message) for w in caught]
    return list(dict.fromkeys(out))


def source_of(value):
    try:
        return inspect.getsource(value)
    except (OSError, TypeError):
        return ""


def warn_calls(source):
    """Text of the arguments of every warnings.warn(...) call, with string pieces joined."""
    out = []
    for m in re.finditer(r"warnings\.warn\(", source):
        depth, i = 1, m.end()
        while i < len(source) and depth:
            depth += {"(": 1, ")": -1}.get(source[i], 0)
            i += 1
        call = source[m.end():i - 1]
        pieces = re.findall(r"[rfb]?\"((?:[^\"\\]|\\.)*)\"|[rfb]?'((?:[^'\\]|\\.)*)'", call)
        text = " ".join(a or b for a, b in pieces).strip()
        if text:
            out.append(" ".join(text.split()))
    return out


def deprecated_notes(doc):
    out = []
    for m in re.finditer(r"\.\. deprecated::([^\n]*)\n((?:[ \t]+[^\n]*\n?)*)", doc or ""):
        out.append(" ".join((m.group(1) + " " + m.group(2)).split()))
    return out


def parameter_doc(doc, param):
    m = re.search(rf"^\s*{re.escape(param)}\s*:[^\n]*\n((?:[ \t]{{5,}}[^\n]*\n?)*)", doc or "", re.M)
    return " ".join(m.group(0).split()) if m else ""


def main():
    library = sys.argv[1]
    warnings.simplefilter("ignore")
    objs = targets(library)
    rows = list(csv.DictReader(open(os.path.join(RESULTS, f"{library}_api_diff.csv"), encoding="utf-8")))
    out = []
    for r in rows:
        tname = r["seen_on"].split()[0]
        obj, sample = objs.get(tname, (None, None))
        name, param = r["name"], r["parameter"]
        rec = {"change": r["change"], "defined_in": r["defined_in"], "name": name, "parameter": param,
               "candidate": r["candidate"], "warning": "", "source": "", "docstring": ""}
        if obj is None:
            out.append(rec)
            continue
        if not param:
            rec["warning"] = " | ".join(warns_on_access(obj, name, sample))
        try:
            value = inspect.getattr_static(obj, name)
        except AttributeError:
            value = getattr(obj, name, None)
        if isinstance(value, (staticmethod, classmethod)):
            value = value.__func__
        if isinstance(value, property):
            value = value.fget
        src = source_of(value) if value is not None else ""
        doc = getattr(value, "__doc__", "") or ""
        if param:
            rec["source"] = " | ".join(w for w in warn_calls(src) if param in w)
            rec["docstring"] = parameter_doc(doc, param)
        else:
            rec["source"] = " | ".join(warn_calls(src))
            rec["docstring"] = " | ".join(deprecated_notes(doc))
        out.append(rec)
    path = os.path.join(RESULTS, f"{library}_deprecations.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    found = sum(1 for o in out if o["warning"] or o["source"] or o["docstring"])
    print(f"{library}: {len(out)} rows, {found} with a message in the old version -> {path}")


if __name__ == "__main__":
    main()
