"""Selection criteria applied to the rows of the candidate pool (used by build_pool.py).

Criterion 1 (public API). The scope of the API comparison already follows each library's definition
of its public API (see README.md). Within that scope, a row is still not public if the library itself
marks it as not public, or if it is not an object of the library:
  - NumPy 1.23.5 lists, in numpy/tests/test_public_api.py (test_numpy_namespace), the objects of the
    main namespace that are "not publicly documented to be part of the main NumPy namespace", and
    lists numpy.compat and numpy.linalg.lapack_lite as private modules (PRIVATE_BUT_PRESENT_MODULES);
  - numpy.math, numpy.os, numpy.sys and numpy.warnings are modules of the Python standard library;
  - numpy.oldnumeric and numpy.numarray are the string 'removed', left behind as placeholders.
Two of the earlier test cases are not public API for the same reasons (EARLIER_NOT_PUBLIC).

Criterion 4 (no extra packages). A row fails if the old code or its replacement needs a package that
is not installed with pandas and NumPy: openpyxl (Excel), PyTables (HDFStore), matplotlib (plotting),
jinja2 (Styler, and LaTeX output in pandas 2.x), lxml (read_html, read_xml), pyarrow (Arrow-backed
arrays), tabulate (to_markdown) or nose (NumPy's old nose support).
"""

NUMPY_NOT_PUBLIC = {  # test_numpy_namespace in NumPy 1.23.5
    "Tester", "add_docstring", "add_newdoc", "add_newdoc_ufunc", "byte_bounds", "compare_chararrays",
    "deprecate", "deprecate_with_doc", "disp", "fastCopyAndTranspose", "get_array_wrap", "get_include",
    "recfromcsv", "recfromtxt", "safe_eval", "set_string_function", "show_config", "who",
}
NUMPY_PRIVATE_MODULES = {("numpy", "compat"), ("numpy.linalg", "lapack_lite")}
NUMPY_STDLIB = {"math", "os", "sys", "warnings"}
NUMPY_PLACEHOLDERS = {"oldnumeric", "numarray"}
EARLIER_NOT_PUBLIC = {
    "P55": "pandas.io.json.json_normalize is not in the pandas API reference",
    "N31": "listed as not publicly documented in NumPy 1.23.5 (test_public_api.py)",
}

EXTRA_BY_CLASS = {"ExcelWriter": "openpyxl", "ExcelFile": "openpyxl", "HDFStore": "PyTables",
                  "ArrowExtensionArray": "pyarrow"}
EXTRA_BY_FUNCTION = {"read_excel": "openpyxl", "to_excel": "openpyxl", "to_latex": "jinja2"}
EXTRA_BY_MEMBER = {("BaseGroupBy", "plot"): "matplotlib", ("pandas.plotting", "table"): "matplotlib",
                   ("numpy.testing", "Tester"): "nose", ("numpy.testing", "dec"): "nose",
                   ("numpy.testing", "raises"): "nose", ("numpy.testing", "run_module_suite"): "nose"}
EXTRA_BY_ENTRY = {  # release-note entries
    "pandas-2.0.0-L865": "jinja2", "pandas-2.0.0-L866": "jinja2", "pandas-2.0.0-L867": "jinja2",
    "pandas-2.0.0-L868": "jinja2", "pandas-2.0.0-L870": "jinja2",  # Styler
    "pandas-2.0.0-L900": "matplotlib",  # plot(sort_columns)
    "pandas-2.0.0-L989": "openpyxl", "pandas-2.0.0-L1064": "openpyxl",  # ExcelWriter
    "pandas-2.0.0-L1001": "tabulate",  # to_markdown(showindex)
    "pandas-2.0.0-L1045": "jinja2",  # to_latex
    "pandas-2.0.0-L913": "openpyxl",  # read_excel
    "pandas-2.0.0-L933": "lxml",  # read_html
    "pandas-2.0.0-L940": "lxml",  # read_xml, default parser
    # display.latex.* options: their replacements (styler.*) only affect LaTeX output, which needs jinja2
    "pandas-2.0.0-L627": "jinja2", "pandas-2.0.0-L628": "jinja2", "pandas-2.0.0-L629": "jinja2",
    "pandas-2.0.0-L633": "jinja2",
}


def criterion_1(row):
    """('yes' or 'no', reason) for a pool row; api is the row of the API comparison, if any."""
    api = row.get("api")
    if api and api["library"] == "numpy" and api["change"] == "removed attribute":
        owner, name = api["defined_in"], api["name"]
        if owner == "numpy" and name in NUMPY_NOT_PUBLIC:
            return "no", "listed as not publicly documented in NumPy 1.23.5 (test_public_api.py)"
        if (owner, name) in NUMPY_PRIVATE_MODULES:
            return "no", "a private module in NumPy 1.23.5 (test_public_api.py)"
        if owner == "numpy" and name in NUMPY_STDLIB:
            return "no", "a module of the Python standard library, not part of NumPy"
        if owner == "numpy" and name in NUMPY_PLACEHOLDERS:
            return "no", "the string 'removed', a placeholder"
    return "yes", ""


def criterion_4(row):
    """('yes' or 'no', the extra package) for a pool row."""
    api = row.get("api")
    if api:
        package = (EXTRA_BY_CLASS.get(api["defined_in"]) or EXTRA_BY_FUNCTION.get(api["name"])
                   or EXTRA_BY_MEMBER.get((api["defined_in"], api["name"])))
        if package:
            return "no", package
    package = EXTRA_BY_ENTRY.get(row.get("entry", ""))
    if package:
        return "no", package
    return "yes", ""
