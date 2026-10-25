"""Compare every reproduced number with the number written in the thesis draft.

Reads results/*.json and data/changes.csv; writes results/summary.md.
A row is marked "yes" when the result of this run equals the draft's number, "NO" otherwise.
"""
import json
import os
import re

from changes import load_changes

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
RES = os.path.join(ROOT, "results")
HINT = re.compile(r"\b(use|instead)\b|might want to try", re.I)
TEMPLATE_E3 = re.compile(r"^AttributeError: `[^`]+` was removed in the NumPy 2\.0 release\. Use `[^`]+` instead\.$")
NO_FIX_IN_ENTRY = ["P05", "P06", "P07", "P24", "P26", "P27", "P28", "P31", "P32", "P33", "P39", "P44", "P54"]
TYPES = ("removed API", "removed parameter", "behavior change (raises)", "silent change")


def load(name):
    return json.load(open(os.path.join(RES, name), encoding="utf-8"))


def clean(msg):
    msg = re.sub(r"^(?:[A-Za-z_]\w*\.)+(?=[A-Za-z_]\w*(?:Error|Exception))", "", (msg or "").strip())
    msg = re.sub(r"\(/[^)]*\)", "", msg)
    msg = re.sub(r"\(<site-packages path>\)", "", msg)
    return " ".join(msg.split())


def main():
    ch = load_changes()
    cand = {r["id"]: r for r in load("candidates.json")}
    pilot = load("pilot.json")
    ruff = load("ruff.json")
    sugg = load("suggestions.json")
    extra = load("extra.json")
    notes = load("release_notes.json")
    p313 = load("py313.json")

    rows = []

    def check(section, item, expected, got):
        rows.append((section, item, str(expected), str(got), "yes" if str(expected) == str(got) else "NO"))

    def lib(ids, prefix):
        return sum(1 for i in ids if i.startswith(prefix))

    # --- 1 introduction ---
    check("1", "pandas 2.0.0 release notes: entries under 'Removal of prior version deprecations/changes'", 233, notes["entries"])

    # --- 3.2.2 candidates ---
    kinds = {k: [i for i, r in cand.items() if r["kind"] == k] for k in ("raises", "silent", "same")}
    check("3.2.2, Table 1", "candidate changes", 100, len(cand))
    check("3.2.2, Table 1", "raise an error (pandas / NumPy / total)", "55 / 38 / 93", f"{lib(kinds['raises'], 'P')} / {lib(kinds['raises'], 'N')} / {len(kinds['raises'])}")
    check("3.2.2, Table 1", "change results silently (pandas / NumPy / total)", "4 / 1 / 5", f"{lib(kinds['silent'], 'P')} / {lib(kinds['silent'], 'N')} / {len(kinds['silent'])}")
    check("3.2.2, Table 1", "behave the same (pandas / NumPy / total)", "1 / 1 / 2", f"{lib(kinds['same'], 'P')} / {lib(kinds['same'], 'N')} / {len(kinds['same'])}")
    agree = sum(1 for i, r in cand.items() if ch[i]["observed"] == r["kind"])
    check("3.2.2", "candidates classified as recorded in changes.csv", 100, agree)
    msg_ok = sum(1 for i in kinds["raises"] if clean(cand[i]["new_message"]).startswith(clean(ch[i]["new_error_or_change"])[:60]))
    check("3.2.2", "error messages identical to the recorded ones (first 60 characters)", len(kinds["raises"]), msg_ok)

    selected = [i for i in ch if ch[i]["decision"] == "included"]
    readmit = [i for i in ch if ch[i]["reason"] == "rarely used"]
    planned = selected + readmit
    check("3.2.2", "selected changes (pandas / NumPy / total)", "46 / 29 / 75", f"{lib(selected, 'P')} / {lib(selected, 'N')} / {len(selected)}")
    types = [sum(1 for i in selected if ch[i]["change_type"] == t) for t in TYPES]
    check("3.2.2", "selected changes by type (removed API / removed parameter / behavior change / silent)", "46 / 19 / 6 / 4", " / ".join(map(str, types)))
    ptypes = [sum(1 for i in planned if ch[i]["change_type"] == t) for t in TYPES]
    check("3.2.2", "the 86 planned changes by type (removed API / removed parameter / behavior change / silent)", "55 / 21 / 6 / 4", " / ".join(map(str, ptypes)))
    rep_sel = sum(1 for i in selected if cand[i]["replacement"] == "same values")
    rep_re = sum(1 for i in readmit if cand[i]["replacement"] == "same values")
    check("3.2.2", "selected 75: replacement gives the same values as the old call", 75, rep_sel)
    check("3.2.2", "re-admitted 11: replacement gives the same values as the old call", 11, rep_re)

    # --- 3.3 hint rule ---
    err71 = [i for i in selected if cand[i]["kind"] == "raises"]
    err11 = [i for i in readmit if cand[i]["kind"] == "raises"]
    err82 = err71 + err11
    hint = {i: bool(HINT.search(cand[i]["new_message"] or "")) for i in err82}
    check("3.3", "selected changes that raise an error", 71, len(err71))
    check("3.3", "of these 71: with hint / without hint", "23 / 48", f"{sum(hint[i] for i in err71)} / {sum(not hint[i] for i in err71)}")
    same_lab = sum(1 for i in err71 if ("yes" if hint[i] else "no") == ch[i]["hint_in_error"])
    check("3.3", "hint rule agrees with the recorded label", "71 / 71", f"{same_lab} / 71")
    check("3.3", "re-admitted 11: NumPy with hint / pandas with hint", "7 of 7 / 0 of 4",
          f"{sum(hint[i] for i in err11 if i[0] == 'N')} of {lib(err11, 'N')} / {sum(hint[i] for i in err11 if i[0] == 'P')} of {lib(err11, 'P')}")
    check("3.3, Table 4", "of the 82: with hint / without hint", "30 / 52", f"{sum(hint.values())} / {sum(not v for v in hint.values())}")
    check("5.3, Table 4", "pandas: with hint / erroring changes", "1 / 47", f"{sum(hint[i] for i in err82 if i[0] == 'P')} / {lib(err82, 'P')}")
    check("5.3, Table 4", "NumPy: with hint / erroring changes", "29 / 35", f"{sum(hint[i] for i in err82 if i[0] == 'N')} / {lib(err82, 'N')}")
    check("5.3", "of the 71: pandas 1/43, NumPy 22/28", "1/43, 22/28",
          f"{sum(hint[i] for i in err71 if i[0] == 'P')}/{lib(err71, 'P')}, {sum(hint[i] for i in err71 if i[0] == 'N')}/{lib(err71, 'N')}")
    params = [i for i in err82 if ch[i]["change_type"] == "removed parameter"]
    check("5.3", "removed parameters: with hint / total", "0 / 21", f"{sum(hint[i] for i in params)} / {len(params)}")

    # --- 5.4 interpreter suggestions ---
    with_s = {k: v["suggestion"] for k, v in sugg.items() if v["suggestion"]}
    check("5.4", "attribute errors", 54, len(sugg))
    check("5.4", "with a 'Did you mean' suggestion", 9, len(with_s))
    check("5.4", "suggestions", "N15 cumprod, P01 _append, P02 _append, P03 isetitem, P09 _join_monotonic, P14 _mode, P26 map, P27 map, P28 shift",
          ", ".join(f"{k} {v}" for k, v in sorted(with_s.items())))
    e0e2 = sum(1 for i in err82 if not hint[i] and i not in with_s)
    check("3.4", "changes whose E0 equals E2 (no library hint, no interpreter suggestion)", 43, e0e2)
    e0e3 = sum(1 for i in err82 if TEMPLATE_E3.match((cand[i]["new_message"] or "").strip()))
    check("3.4 / 3.7", "NumPy changes whose E0 already has the E3 template form (about 20)", 20, e0e3)

    # --- 3.5 D2: old deprecation warnings ---
    warned = [i for i in NO_FIX_IN_ENTRY if cand[i]["old_warnings"]]
    check("3.5", "13 pandas changes whose release-note entry names no fix: old version warns", 13, len(warned))

    # --- 5.2-5.3 pilot ---
    check("5.2", "pilot cases passing all four checks", "9 / 9", f"{sum(r['verified'] for r in pilot)} / {len(pilot)}")
    wrong = [r for r in pilot if r["wrong_fix"]]
    check("5.2", "wrong fixes caught by the test", "3 / 3", f"{sum(r['wrong_fix'] == 'caught' for r in wrong)} / {len(wrong)}")
    err_p = [r for r in pilot if r["raises"]]
    check("5.3", "pilot cases that raise / with hint (NumPy only?)", "8 / 3 (NumPy only)",
          f"{len(err_p)} / {sum(r['has_hint'] for r in err_p)} ({'NumPy only' if all(r['library'].lower() == 'numpy' for r in err_p if r['has_hint']) else 'mixed'})")
    pd_cases = [r for r in pilot if r["library"].lower() == "pandas"]
    check("5.4", "pilot pandas errors with 'Did you mean'", "2 / 4", f"{sum(r['did_you_mean'] for r in pd_cases)} / {len(pd_cases)}")

    # --- 5.5 Ruff ---
    rc = ruff["cases"]
    check("5.5", "Ruff version", "ruff 0.16.10", ruff["ruff_version"])
    check("5.5", "Ruff detected / fixed", "4 / 3", f"{sum(r['detected'] for r in rc)} / {sum(r['fixed'] for r in rc)}")
    check("5.5", "cases fixed by Ruff", "C5, C6, C7", ", ".join(r["case"][:2] for r in rc if r["fixed"]))
    check("5.5", "pandas cases detected by Ruff", 0, sum(r["detected"] for r in rc if "pandas" in r["case"]))

    # --- small checks ---
    envs_ok = all(v.get("python", "").startswith("3.11") and v.get("runs") for v in extra["envs"].values())
    check("3.2.1", "all three library combinations run under Python 3.11", True, envs_ok)
    check("3.9 / 5.4", "a fix calling the private _append passes the pilot test", True, extra["private_append_passes_test"])
    check("Table 2", "a fix following the E4 suggestion 'apply' passes the pilot test", False, extra["e4_apply_passes_test"])
    check("5.4", "keyword and import errors carry no 'Did you mean' (Python 3.11)", True,
          "Did you mean" not in extra["keyword_error"] and "Did you mean" not in extra["import_error"])

    # --- 7 Python 3.13 (numbers to be added to Chapter 7) ---
    fol = p313["follow_keyword_suggestion"]
    check("7 (to be added)", "of the 82 error messages, different under Python 3.13", 7, len(p313["differ"]))
    check("7 (to be added)", "new keyword-name suggestions under Python 3.13", 5, len(fol))
    check("7 (to be added)", "following them: correct / fails / wrong result", "3 / 1 / 1",
          f"{sum(v == 'same as old' for v in fol.values())} / {sum(v == 'fails' for v in fol.values())} / {sum(v == 'different result' for v in fol.values())}")

    ok = sum(r[4] == "yes" for r in rows)
    lines = ["# Reproduced numbers compared with the thesis draft", "",
             f"{ok} of {len(rows)} items match the draft; {len(rows) - ok} differ.", "",
             "Environments: " + "; ".join(f"{k}: Python {v.get('python')}, pandas {v.get('pandas')}, NumPy {v.get('numpy')}" for k, v in extra["envs"].items()), "",
             "| Draft section | Item | Draft | This run | Match |", "| --- | --- | --- | --- | --- |"]
    lines += [f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in rows]
    diff_rep = [i for i in planned if cand[i]["replacement"] != "same values"]
    if diff_rep:
        lines += ["", "Planned changes whose replacement does not give the old values: " + ", ".join(f"{i} ({cand[i]['replacement']})" for i in diff_rep)]
    open(os.path.join(RES, "summary.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
