"""Static validity checks on a fix (Section 3.9).

A fix that passes the tests is correct only if it also passes these checks:
  1. no name that starts with an underscore taken from pandas or NumPy: no import from a private module
     (pandas._libs) or of a private name, and no attribute access such as df._append. The objects in the
     test case programs are pandas and NumPy objects, so every attribute that starts with a single
     underscore counts, except on self and cls; dunder names are allowed;
  2. no assignment to an attribute of a library object (monkey-patching), such as pd.DataFrame.append = ...;
  3. no bare or broad except clause (except:, except Exception, except BaseException) and no warning
     filter (warnings.filterwarnings, warnings.simplefilter, warnings.catch_warnings) beyond those already
     in the old code.

check(fix, old) returns the list of violations; an empty list means the fix is valid.
"""
import ast

LIBRARIES = {"pandas", "numpy"}
BROAD = {"Exception", "BaseException"}
WARNING_FILTERS = {"filterwarnings", "simplefilter", "catch_warnings"}


def _private(name):
    return name.startswith("_") and not (name.startswith("__") and name.endswith("__"))


def _library_aliases(tree):
    aliases = set(LIBRARIES)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] in LIBRARIES:
                    aliases.add(a.asname or a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] in LIBRARIES:
            for a in node.names:
                aliases.add(a.asname or a.name)
    return aliases


def _root(node):
    while isinstance(node, (ast.Attribute, ast.Subscript, ast.Call)):
        node = node.func if isinstance(node, ast.Call) else node.value
    return node.id if isinstance(node, ast.Name) else None


def _broad_and_filters(tree):
    broad, filters = 0, 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            names = []
            if node.type is None:
                names = ["bare"]
            elif isinstance(node.type, ast.Tuple):
                names = [e.id for e in node.type.elts if isinstance(e, ast.Name)]
            elif isinstance(node.type, ast.Name):
                names = [node.type.id]
            broad += any(n == "bare" or n in BROAD for n in names)
        elif isinstance(node, ast.Attribute) and node.attr in WARNING_FILTERS:
            filters += 1
        elif isinstance(node, ast.ImportFrom) and node.module == "warnings":
            filters += sum(a.name in WARNING_FILTERS for a in node.names)
    return broad, filters


def check(fix, old=""):
    try:
        tree = ast.parse(fix)
    except SyntaxError as e:
        return [f"syntax error: {e.msg} (line {e.lineno})"]
    problems = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and _private(node.attr) and _root(node) not in ("self", "cls"):
            problems.append(f"private name .{node.attr} (line {node.lineno})")
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            modules = [node.module or ""] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names]
            for m in modules:
                parts = m.split(".")
                if parts[0] in LIBRARIES and any(_private(p) for p in parts[1:]):
                    problems.append(f"private module {m} (line {node.lineno})")
            if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] in LIBRARIES:
                problems += [f"private name {a.name} (line {node.lineno})" for a in node.names if _private(a.name)]
    aliases = _library_aliases(tree)
    for node in ast.walk(tree):
        targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(
            node, (ast.AugAssign, ast.AnnAssign)) else []
        for t in targets:
            if isinstance(t, ast.Attribute) and _root(t) in aliases:
                problems.append(f"assignment to a library attribute (line {t.lineno})")
    broad, filters = _broad_and_filters(tree)
    old_broad, old_filters = (0, 0)
    if old:
        try:
            old_broad, old_filters = _broad_and_filters(ast.parse(old))
        except SyntaxError:
            pass
    if broad > old_broad:
        problems.append("added bare or broad except clause")
    if filters > old_filters:
        problems.append("added warning filter")
    return problems
