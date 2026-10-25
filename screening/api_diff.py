"""Compare the API listings of an old and a new version of one library and write the differences.

usage: python screening/api_diff.py OLD.json NEW.json OUT.csv

Each output row is one candidate change for the candidate pool:
  removed attribute  a member listed in the old version that cannot be accessed in the new one
  removed parameter  a callable present in both versions whose old parameter is gone

A change is listed once per class that defines it. For example, Index.is_monotonic is one row, not
one row each for Index, DatetimeIndex, RangeIndex and the other subclasses that inherit it; the
column seen_on lists where the member was found. Members of classes that were removed as a whole
are not listed separately.

The column candidate gives the id of the change in measurements/data/changes.csv when the row is
one of the 100 candidates.
"""
import csv
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CHANGES = os.path.join(ROOT, "measurements", "data", "changes.csv")

# Temporary variables that numpy/__init__.py of NumPy 1.23.5 leaves behind on some platforms only:
# w and error_message from the macOS check, kernel_version from the Linux check. They are not part
# of the API, and keeping them would make the result depend on the computer.
PLATFORM_LEFTOVERS = {("numpy", "w"), ("numpy", "error_message"), ("numpy", "kernel_version")}

# variable names used in changes.csv -> inspected object
PREFIX = [("dtindex.", "DatetimeIndex"), ("pd.api.types.", "pandas.api.types"), ("df.", "DataFrame"),
          ("s.", "Series"), ("idx.", "Index"), ("cat.", "Categorical"), ("arr.", "ndarray"),
          ("ts.", "Timestamp"), ("pd.", "pandas"), ("np.", "numpy")]


def load(path):
    return json.load(open(path, encoding="utf-8"))


def owner_of(tname, target, name):
    """Group key for a member: the defining class for classes, the module itself for modules."""
    member = target["members"][name]
    return member.get("defined_in", tname)


def differences(old, new):
    rows = {}
    for tname, ot in old["targets"].items():
        if tname not in new["targets"]:
            continue  # a class removed as a whole is one row, under the module that exposed it
        nt = new["targets"][tname]
        gone = set(nt.get("still_accessible", []))
        for name, om in ot["members"].items():
            if name not in nt["members"]:
                if name in gone or (tname, name) in PLATFORM_LEFTOVERS:
                    continue
                key = ("removed attribute", owner_of(tname, ot, name), name, "")
                row = rows.setdefault(key, {"kind": om["kind"], "hidden_in_old": bool(om.get("hidden")),
                                            "seen_on": [], "accepts_any_keyword": ""})
                row["seen_on"].append(tname)
                continue
            nm = nt["members"][name]
            if "params" not in om or "params" not in nm:
                continue
            for p in om["params"]:
                if p in nm["params"]:
                    continue
                key = ("removed parameter", owner_of(tname, ot, name), name, p)
                row = rows.setdefault(key, {"kind": om["kind"], "hidden_in_old": False, "seen_on": [],
                                            "accepts_any_keyword": "yes" if nm.get("accepts_any_keyword") else ""})
                row["seen_on"].append(tname)
    return rows


def candidate_keys():
    """(change, inspected object, member, parameter) for each removed API or parameter in changes.csv."""
    keys = []
    with open(CHANGES, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            err, usage = r["new_error_or_change"], r["old_usage"]
            if r["change_type"] == "removed API":
                m = (re.search(r"'(\w+)' object has no attribute '(\w+)'", err)
                     or re.search(r"module '([\w.]+)' has no attribute '(\w+)'", err))
                if m:
                    keys.append((r["id"], "removed attribute", m.group(1), m.group(2), ""))
                    continue
                m = re.search(r"`np\.(\w+)` was removed", err)
                if m:
                    keys.append((r["id"], "removed attribute", "numpy", m.group(1), ""))
                    continue
                m = re.search(r"`(\w+)` was removed from the ndarray class", err)
                if m:
                    keys.append((r["id"], "removed attribute", "ndarray", m.group(1), ""))
                    continue
                keys.append((r["id"], "removed attribute", None, None, ""))
            elif r["change_type"] == "removed parameter":
                m = re.search(r"unexpected keyword argument '(\w+)'", err)
                target = next((t for p, t in PREFIX if usage.startswith(p)), None)
                prefix = next((p for p, t in PREFIX if usage.startswith(p)), "")
                member = re.match(r"(\w+)", usage[len(prefix):])
                keys.append((r["id"], "removed parameter", target, member.group(1) if member else None,
                             m.group(1) if m else None))
    return keys


def main():
    old_path, new_path, out_path = sys.argv[1:4]
    old, new = load(old_path), load(new_path)
    rows = differences(old, new)
    # class name in an error message -> inspected object (DataFrame, not pandas.api.interchange.DataFrame)
    type_names = {}
    for t, e in old["targets"].items():
        if t == e["type_name"] or e["type_name"] not in type_names:
            type_names[e["type_name"]] = t

    matched = {}
    unmatched = []
    for cid, change, target, member, param in candidate_keys():
        if (cid[0] == "P") != (old["library"] == "pandas"):
            continue
        target = type_names.get(target, target)
        hit = [k for k, v in rows.items() if k[0] == change and target in v["seen_on"]
               and k[2] == member and k[3] == param]
        for k in hit:
            matched.setdefault(k, []).append(cid)
        if not hit:
            unmatched.append(cid)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["library", "change", "defined_in", "name", "parameter", "kind", "seen_on",
                    "hidden_in_old", "new_accepts_any_keyword", "candidate"])
        for key in sorted(rows):
            v = rows[key]
            w.writerow([old["library"], key[0], key[1], key[2], key[3], v["kind"], " ".join(v["seen_on"]),
                        "yes" if v["hidden_in_old"] else "", v["accepts_any_keyword"],
                        " ".join(matched.get(key, []))])

    n_attr = sum(1 for k in rows if k[0] == "removed attribute")
    n_par = len(rows) - n_attr
    print(f"{old['library']} {old[old['library']]} -> {new[new['library']]}: "
          f"{n_attr} removed attributes, {n_par} removed parameters -> {out_path}")
    print(f"  rows that are candidates: {len(matched)}; candidates of these two types not found: "
          f"{' '.join(unmatched) if unmatched else 'none'}")


if __name__ == "__main__":
    main()
