"""Build the candidate pool: one row per change, from both sources, with a column for each criterion.

usage: python screening/build_pool.py
Reads results/pandas_api_diff.csv, results/numpy_api_diff.csv, results/release_note_decisions.csv
and measurements/data/changes.csv; writes results/pool.csv.

Row ids:  A-P-nnn / A-N-nnn  rows of the API comparison (pandas / NumPy)
          R-P-nnn / R-N-nnn  release-note entries that add a pool row
          C-xxx              candidates of changes.csv that neither source lists (kept so that every
                             earlier decision has a row)

Rows of the 100 earlier candidates carry the earlier decision, so they are not examined again. For
the other rows, criteria 1 and 4 are applied here (criteria.py); a row that fails one is excluded.
The columns of criteria 3 and 2 are filled in the next steps.
"""
import csv
import os

from criteria import criterion_1, criterion_4

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
RESULTS = os.path.join(HERE, "results")

COLUMNS = ["id", "source", "library", "change", "candidate", "entry",
           "c1_public", "c4_no_extra_package", "c3_replacement", "c3_source",
           "c2_old_code", "c2_raises_in_new", "c3_new_code", "c3_same_result",
           "decision", "reason"]
DUPLICATES = {"pandas-2.0.0-L1066": "pandas-2.0.0-L892"}  # same change, two entries


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def earlier_decision(cid, changes):
    """Decision recorded for an earlier candidate, under the current criteria."""
    c = changes[cid]
    if c["observed"] != "raises":
        return "excluded", f"earlier candidate: {c['observed']} in the new version (no error)"
    if c["decision"] == "included" or c["reason"] == "rarely used":
        return "included", "earlier candidate: test case"
    return "excluded", f"earlier candidate: {c['reason']}"


def main():
    changes = {r["id"]: r for r in read(os.path.join(ROOT, "measurements", "data", "changes.csv"))}
    pool = []

    for lib, short in (("pandas", "P"), ("numpy", "N")):
        for n, r in enumerate(read(os.path.join(RESULTS, f"{lib}_api_diff.csv")), 1):
            name = f"{r['defined_in']}.{r['name']}" + (f"({r['parameter']}=...)" if r["parameter"] else "")
            pool.append({"id": f"A-{short}-{n:03d}", "source": "API comparison", "library": lib,
                         "change": f"{r['change']}: {name}", "candidate": r["candidate"], "entry": "",
                         "api": r})

    counters = {"pandas": 0, "numpy": 0}
    for r in read(os.path.join(RESULTS, "release_note_decisions.csv")):
        if r["category"] not in ("removal", "raises", "api+removal") or r["entry"] in DUPLICATES:
            continue
        counters[r["library"]] += 1
        short = "P" if r["library"] == "pandas" else "N"
        pool.append({"id": f"R-{short}-{counters[r['library']]:03d}", "source": "release notes",
                     "library": r["library"], "change": f"{r['category']}: {r['note']}",
                     "candidate": r["candidates"], "entry": r["entry"]})

    listed = {c for row in pool for c in row["candidate"].split()}
    for cid, c in changes.items():
        if cid in listed or c["observed"] != "raises":
            continue
        pool.append({"id": f"C-{cid}", "source": "earlier candidate", "library": c["library"].lower(),
                     "change": f"{c['change_type']}: {c['old_usage']}", "candidate": cid, "entry": ""})

    for row in pool:
        for col in COLUMNS:
            row.setdefault(col, "")
        ids = row["candidate"].split()
        if ids:
            decisions = [earlier_decision(i, changes) for i in ids]
            included = [d for d in decisions if d[0] == "included"]
            row["decision"], row["reason"] = included[0] if included else decisions[0]
            continue
        row["c1_public"], why1 = criterion_1(row)
        row["c4_no_extra_package"], why4 = criterion_4(row)
        if row["c1_public"] == "no":
            row["decision"], row["reason"] = "excluded", f"criterion 1: {why1}"
        elif row["c4_no_extra_package"] == "no":
            row["decision"], row["reason"] = "excluded", f"criterion 4: needs {why4}"

    out = os.path.join(RESULTS, "pool.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(pool)

    done = [r for r in pool if r["decision"]]
    print(f"{len(pool)} pool rows -> {out}")
    for src in ("API comparison", "release notes", "earlier candidate"):
        rows = [r for r in pool if r["source"] == src]
        early = [r for r in rows if r["candidate"]]
        c1 = [r for r in rows if r["c1_public"] == "no"]
        c4 = [r for r in rows if r["c1_public"] != "no" and r["c4_no_extra_package"] == "no"]
        print(f"  {src:17s} {len(rows):3d} rows: {len(early):2d} decided earlier, {len(c1):2d} fail criterion 1, "
              f"{len(c4):2d} fail criterion 4, {len(rows) - len(early) - len(c1) - len(c4):3d} to examine")
    inc = sorted({c for r in done if r["decision"] == "included" for c in r["candidate"].split()
                  if earlier_decision(c, changes)[0] == "included"})
    print(f"  earlier test cases with a row: {len(inc)}")


if __name__ == "__main__":
    main()
