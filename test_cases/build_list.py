"""Build the list of test cases: the earlier test cases that still meet the criteria, plus the changes
drawn from the candidate pool.

usage: python test_cases/build_list.py
Reads measurements/data/changes.csv, measurements/scripts/candidates_spec.py, screening/results/pool.csv,
screening/results/draw.csv and screening/results/pool_checks.csv; writes test_cases/list.csv.

changes.csv records the decisions on the 100 earlier candidates under the criteria of the proposal of
October 6. The screening of the candidate pool applies the criteria as now defined; under it, two of
the 82 earlier test cases are not public API and are left out (NOT_PUBLIC, from screening/criteria.py).
The changes drawn from the pool get the next free ids (P61 onward, N41 onward).
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "measurements", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "screening"))
from candidates_spec import SPEC  # noqa: E402
from changes import is_planned, load_changes  # noqa: E402
from criteria import EARLIER_NOT_PUBLIC as NOT_PUBLIC  # noqa: E402
from pool_spec import SPEC as POOL_SPEC  # noqa: E402

# The drawn changes, described as in changes.csv.
DRAWN = {
    "A-N-129": ("N41", "removed parameter", "np.histogram2d(x, y, normed=True)", "np.histogram2d(x, y, density=True)",
                "1.24", "NumPy 1.24.0 release notes, 1.24.0-notes.rst, line 82"),
    "A-P-011": ("P61", "removed API", "cat.take_nd(indexer)", "cat.take(indexer)",
                "2.0", "pandas 2.0.0 release notes, v2.0.0.rst, line 845"),
    "A-P-023": ("P62", "removed API", "pd.array(dtindex).weekofyear", "pd.array(dtindex).isocalendar().week",
                "2.0", "pandas 2.0.0 release notes, v2.0.0.rst, line 862"),
    "A-P-088": ("P63", "removed parameter", "df.any(level=0)", "df.groupby(level=0).any()",
                "2.0", "pandas 2.0.0 release notes, v2.0.0.rst, line 958"),
    "A-P-150": ("P64", "removed parameter", "pidx.get_loc(key, method='nearest')",
                "pidx.get_indexer([key], method='nearest')[0]", "2.0",
                "pandas 2.0.0 release notes, v2.0.0.rst, line 978"),
    "A-P-174": ("P65", "removed parameter", "s.sem(level=0)", "s.groupby(level=0).sem()",
                "2.0", "pandas 2.0.0 release notes, v2.0.0.rst, line 958"),
    "A-P-194": ("P66", "removed parameter", "pd.lreshape(data, groups, label=...)", "remove the label argument",
                "2.0", "pandas 2.0.0 release notes, v2.0.0.rst, line 1067"),
    "R-P-041": ("P67", "behavior change (raises)", "df.set_index(keys, False) (drop passed by position)",
                "df.set_index(keys, drop=False)", "2.0", "pandas 2.0.0 release notes, v2.0.0.rst, line 917"),
    "R-P-077": ("P68", "behavior change (raises)", "pd.Categorical('a') (a scalar as data)", "pd.Categorical(['a'])",
                "2.0", "pandas 2.0.0 release notes, v2.0.0.rst, line 953"),
    "R-P-085": ("P69", "behavior change (raises)", "s.between(left, right, inclusive=True)",
                "s.between(left, right, inclusive='both')", "2.0", "pandas 2.0.0 release notes, v2.0.0.rst, line 987"),
}
COLUMNS = ["id", "library", "origin", "pool_id", "change_type", "old_usage", "replacement", "changed_in", "source",
           "old_code", "replacement_code", "mode"]


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def pool_key(row):
    """Key of a pool row in screening/pool_spec.py."""
    if row["entry"]:
        return row["entry"]
    name = row["change"].split(": ", 1)[1]
    return name.replace("=...)", ")")


def main():
    changes = load_changes()
    spec = {s["id"]: s for s in SPEC}
    pool = {r["id"]: r for r in read(os.path.join(ROOT, "screening", "results", "pool.csv"))}
    checks = {r["key"]: r for r in read(os.path.join(ROOT, "screening", "results", "pool_checks.csv"))}
    pool_of = {c: r["id"] for r in pool.values() for c in r["candidate"].split()}

    rows = []
    for cid, c in changes.items():
        if not (is_planned(c) and c["observed"] == "raises") or cid in NOT_PUBLIC:
            continue
        s = spec[cid]
        rows.append({"id": cid, "library": c["library"], "origin": "earlier test case", "pool_id": pool_of.get(cid, ""),
                     "change_type": c["change_type"], "old_usage": c["old_usage"], "replacement": c["replacement"],
                     "changed_in": c["changed_in"], "source": c["source"], "old_code": s["code"],
                     "replacement_code": s["alt"], "mode": s.get("mode", "values")})
    for d in read(os.path.join(ROOT, "screening", "results", "draw.csv")):
        cid, ctype, usage, repl, changed_in, source = DRAWN[d["id"]]
        chk = checks[pool_key(d)]
        mode = POOL_SPEC[pool_key(d)]["mode"]
        rows.append({"id": cid, "library": "NumPy" if cid[0] == "N" else "pandas", "origin": "drawn from the pool",
                     "pool_id": d["id"], "change_type": ctype, "old_usage": usage, "replacement": repl,
                     "changed_in": changed_in, "source": source, "old_code": chk["old_code"],
                     "replacement_code": chk["replacement_code"], "mode": mode})
    rows.sort(key=lambda r: (r["id"][0] != "P", r["id"]))

    path = os.path.join(HERE, "list.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    meets = sum(1 for r in pool.values() if r["decision"] == "meets criteria")
    earlier = sum(1 for r in rows if r["origin"] == "earlier test case")
    print(f"{len(rows)} test cases -> {path}")
    for lib in ("pandas", "NumPy"):
        print(f"  {lib}: {sum(1 for r in rows if r['library'] == lib)}")
    print(f"  earlier test cases {earlier}, drawn {len(rows) - earlier}; "
          f"changes in the pool that meet all criteria: {earlier} + {meets} = {earlier + meets}")


if __name__ == "__main__":
    main()
