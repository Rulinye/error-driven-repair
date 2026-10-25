"""Split the breaking-change sections of the release notes into entries (candidate pool, source 2).

usage: python screening/release_note_entries.py
Reads screening/release_notes/*.rst and writes screening/results/release_note_entries.csv.

Only the sections that the maintainers mark as affecting existing code are read:
  pandas  Backwards incompatible API changes, Removal of prior version deprecations/changes,
          Notable bug fixes
  NumPy   NumPy 2.0 Python API removals, Expired deprecations, Compatibility notes, Changes;
          from the NumPy 2.0 migration guide: Changes to NumPy data type promotion, Other changes
Not read: Deprecations (the old code still runs, with a warning), new features, improvements,
performance, bug fixes, C API, and build changes.

An entry is a top-level bullet, or a subsection heading with the text before its first bullet. Each
entry is linked to the rows of the API comparison whose names it mentions, and to the candidate in
measurements/data/changes.csv whose recorded source line falls inside it.
"""
import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
NOTES = os.path.join(HERE, "release_notes")
RESULTS = os.path.join(HERE, "results")

FILES = {  # file: (library, release, sections to read)
    "pandas_2.0.0.rst": ("pandas", "2.0.0", ["Notable bug fixes", "Backwards incompatible API changes",
                                             "Removal of prior version deprecations/changes"]),
    "pandas_2.1.0.rst": ("pandas", "2.1.0", ["Backwards incompatible API changes"]),
    "pandas_2.2.0.rst": ("pandas", "2.2.0", ["Notable bug fixes"]),
    "numpy_1.24.0.rst": ("numpy", "1.24.0", ["Expired deprecations", "Compatibility notes", "Changes"]),
    "numpy_1.25.0.rst": ("numpy", "1.25.0", ["Expired deprecations", "Compatibility notes", "Changes"]),
    "numpy_1.26.0.rst": ("numpy", "1.26.0", []),
    "numpy_2.0.0.rst": ("numpy", "2.0.0", ["NumPy 2.0 Python API removals", "Expired deprecations",
                                           "Compatibility notes", "Changes"]),
    "numpy_2.1.0.rst": ("numpy", "2.1.0", ["Expired deprecations", "Changes"]),
    "numpy_2.0_migration_guide.rst": ("numpy", "2.0 migration guide",
                                      ["Changes to NumPy data type promotion", "Other changes"]),
}
SOURCE_FILE = {  # how changes.csv names the files
    "v2.0.0.rst": "pandas_2.0.0.rst", "1.24.0-notes.rst": "numpy_1.24.0.rst", "2.0.0-notes.rst": "numpy_2.0.0.rst",
}
UNDERLINE = re.compile(r"^([-=~^*\"#+])\1{3,}\s*$")


def headings(lines):
    """[(index of title line, level char)] for every section heading."""
    out = []
    for i in range(1, len(lines)):
        if UNDERLINE.match(lines[i]) and lines[i - 1].strip() and not UNDERLINE.match(lines[i - 1]):
            out.append((i - 1, lines[i].strip()[0]))
    return out


def section_ranges(lines, wanted):
    """{title: (start, end)} for the wanted sections; a section ends at the next heading of its level or above."""
    heads = headings(lines)
    order = []  # heading characters in order of first appearance = level
    for _, c in heads:
        if c not in order:
            order.append(c)
    ranges = {}
    for n, (i, c) in enumerate(heads):
        title = lines[i].strip()
        if title not in wanted:
            continue
        end = len(lines)
        for j, c2 in heads[n + 1:]:
            if order.index(c2) <= order.index(c):
                end = j
                break
        ranges[title] = (i + 2, end)
    return ranges, {i for i, _ in heads}


def clean(text):
    text = re.sub(r":\w+:`~?([^`<]+?)(?:\s*<[^>]+>)?`", r"\1", text)  # :meth:`DataFrame.x` -> DataFrame.x
    text = re.sub(r"\(`gh-\d+ <[^>]+>`__\)", "", text)
    text = re.sub(r"\(:issue:`[\d`, :issue]+`\)", "", text)
    text = text.replace("``", "`")
    return " ".join(text.split())


def names_in(raw):
    found = re.findall(r":\w+:`~?([^`<]+?)(?:\s*<[^>]+>)?`|``([^`]+)``|(?<![`:\w])`([^`<]+)`(?!_)", raw)
    out = []
    for groups in found:
        for g in groups:
            if g:
                out.append(g.strip())
    return out


def entries(fname):
    library, release, wanted = FILES[fname]
    lines = open(os.path.join(NOTES, fname), encoding="utf-8").read().splitlines()
    ranges, head_idx = section_ranges(lines, wanted)
    out = []
    for title, (start, end) in ranges.items():
        current = None
        i = start
        while i < end:
            line = lines[i]
            if i in head_idx:  # subsection heading: starts a paragraph entry
                current = {"line": i + 1, "section": title, "raw": [line.strip()], "heading": True}
                out.append(current)
                i += 2
                continue
            if re.match(r"^[-*] ", line):  # top-level bullet
                current = {"line": i + 1, "section": title, "raw": [line[2:]], "heading": False}
                out.append(current)
            elif current is not None and line.strip() and not line.startswith(".. "):
                if current["heading"] or line.startswith(" "):
                    current["raw"].append(line.strip())
            i += 1
    rows = []
    for e in out:
        raw = " ".join(e["raw"])
        text = clean(raw)
        if e["heading"] and len(e["raw"]) == 1:
            continue  # heading whose content is only bullets
        rows.append({"entry": f"{library}-{release.replace(' ', '-')}-L{e['line']}", "library": library,
                     "release": release, "file": fname, "line": e["line"], "section": e["section"],
                     "names": " ".join(dict.fromkeys(names_in(raw))), "text": text})
    for r, nxt in zip(rows, rows[1:] + [None]):
        r["last_line"] = (nxt["line"] - 1) if nxt and nxt["file"] == r["file"] else r["line"] + 200
    return rows


def main():
    rows = [r for f in FILES for r in entries(f)]

    # link to candidates by recorded source line
    with open(os.path.join(ROOT, "measurements", "data", "changes.csv"), newline="", encoding="utf-8") as f:
        changes = list(csv.DictReader(f))
    for c in changes:
        m = re.search(r"release notes, (\S+), line (\d+)", c["source"])
        if not m or m.group(1) not in SOURCE_FILE:
            continue
        fname, line = SOURCE_FILE[m.group(1)], int(m.group(2))
        for r in rows:
            if r["file"] == fname and r["line"] <= line <= r["last_line"]:
                r.setdefault("candidates", []).append(c["id"])

    # link to the rows of the API comparison by the names an entry mentions
    api = []
    for lib in ("pandas", "numpy"):
        path = os.path.join(RESULTS, f"{lib}_api_diff.csv")
        with open(path, newline="", encoding="utf-8") as f:
            api += [dict(r, library=lib) for r in csv.DictReader(f)]
    for r in rows:
        mentioned = set()
        for n in r["names"].split():
            mentioned.add(n.split(".")[-1].rstrip("()"))
        hits = []
        for a in api:
            if a["library"] != r["library"]:
                continue
            if a["change"] == "removed attribute" and a["name"] in mentioned:
                hits.append(f"{a['defined_in']}.{a['name']}")
            elif a["change"] == "removed parameter" and a["parameter"] in mentioned and a["name"] in mentioned:
                hits.append(f"{a['defined_in']}.{a['name']}({a['parameter']})")
        r["api_rows"] = " ".join(hits)

    os.makedirs(RESULTS, exist_ok=True)
    out = os.path.join(RESULTS, "release_note_entries.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["entry", "library", "release", "section", "line", "api_rows", "candidates", "text"])
        for r in rows:
            w.writerow([r["entry"], r["library"], r["release"], r["section"], r["line"], r["api_rows"],
                        " ".join(r.get("candidates", [])), r["text"]])
    print(f"{len(rows)} entries -> {out}")
    by = {}
    for r in rows:
        by.setdefault((r["library"], r["release"]), [0, 0])
        by[(r["library"], r["release"])][0] += 1
        by[(r["library"], r["release"])][1] += bool(r["api_rows"])
    for (lib, rel), (n, linked) in by.items():
        print(f"  {lib} {rel}: {n} entries, {linked} mention a row of the API comparison")


if __name__ == "__main__":
    main()
