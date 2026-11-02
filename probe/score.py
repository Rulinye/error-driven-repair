"""Score the answers to the knowledge probe (Section 3.8).

usage: python probe/score.py ANSWERS.csv [--hand probe/hand_labels.csv]
       python probe/score.py --self-check

ANSWERS.csv has the columns model, id, sample, answer (five samples per model and test case).
The optional hand labels have the columns model, id, sample, correct (yes or no); they override the
automatic match.

Writes probe/results/answer_labels.csv (one row per answer: the automatic match, whether it must be
checked by hand, and the final label) and probe/results/known.csv (one row per model and test case).
A test case is known to a model if at least three of its five answers are correct. While an answer
that must be checked by hand has no hand label, the test case is "pending".

--self-check runs the matcher on answers whose label is known: the recorded replacement and the
correct hint E3 must match; the misleading name of E4 (and, for the behavior changes, the code that
follows the misleading hint) must not.
"""
import argparse
import csv
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "conditions"))
from questions import REVIEW, SPEC, matches, near  # noqa: E402

SAMPLES = 5
KNOWN_AT = 3


def read(path):
    return list(csv.DictReader(open(path, encoding="utf-8")))


def write(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def self_check():
    from error_variants import BEHAVIOR, E4_EDIT
    cases = {r["id"]: r for r in read(os.path.join(ROOT, "test_cases", "list.csv"))}
    errors = {r["id"]: r for r in read(os.path.join(ROOT, "conditions", "results", "error_conditions.csv"))}
    failures = []
    for cid, case in cases.items():
        e = errors[cid]
        for label, answer in (("replacement", case["replacement"]), ("E3", e["E3"])):
            if not matches(cid, answer):
                failures.append(f"{cid}: the {label} does not match: {answer!r}")
        if cid in REVIEW:
            continue
        wrong = " ".join(new for _, new in E4_EDIT[cid]) if cid in BEHAVIOR else f"Use {e['e4_name']} instead."
        if matches(cid, wrong):
            failures.append(f"{cid}: the misleading fix matches: {wrong!r}")
    checked = len(cases) - len(REVIEW)
    print(f"self-check: {len(cases)} test cases, 2 correct answers each; {checked} misleading answers "
          f"(the {len(REVIEW)} checked by hand are skipped)")
    for f in failures:
        print("  " + f)
    print("self-check passed" if not failures else f"{len(failures)} failures")
    return not failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("answers", nargs="?")
    ap.add_argument("--hand", default=os.path.join(HERE, "hand_labels.csv"))
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()
    if a.self_check:
        sys.exit(0 if self_check() else 1)
    if not a.answers:
        ap.error("ANSWERS.csv is required")
    hand = {}
    if os.path.exists(a.hand):
        hand = {(r["model"], r["id"], r["sample"]): r["correct"] == "yes" for r in read(a.hand)}
    labels, per_case = [], defaultdict(list)
    for r in read(a.answers):
        if r["id"] not in SPEC:
            raise SystemExit(f"unknown test case {r['id']}")
        key = (r["model"], r["id"], r["sample"])
        auto = matches(r["id"], r["answer"])
        review = r["id"] in REVIEW or (not auto and near(r["id"], r["answer"]))
        final = hand.get(key, None if review else auto)
        labels.append(dict(model=r["model"], id=r["id"], sample=r["sample"], auto_match="yes" if auto else "no",
                           check_by_hand="yes" if review else "no",
                           hand_label={True: "yes", False: "no", None: ""}[hand.get(key)],
                           correct={True: "yes", False: "no", None: "pending"}[final], answer=r["answer"]))
        per_case[(r["model"], r["id"])].append(final)
    known = []
    for (model, cid), finals in sorted(per_case.items()):
        if len(finals) != SAMPLES:
            raise SystemExit(f"{model} {cid}: {len(finals)} answers, expected {SAMPLES}")
        correct = sum(f is True for f in finals)
        pending = sum(f is None for f in finals)
        if correct >= KNOWN_AT:
            status = "known"
        elif correct + pending >= KNOWN_AT:
            status = "pending"
        else:
            status = "unknown"
        known.append(dict(model=model, id=cid, correct_answers=correct, pending_answers=pending, label=status))
    write(os.path.join(HERE, "results", "answer_labels.csv"), labels)
    write(os.path.join(HERE, "results", "known.csv"), known)
    for model in sorted({k["model"] for k in known}):
        rows = [k for k in known if k["model"] == model]
        counts = {s: sum(k["label"] == s for k in rows) for s in ("known", "unknown", "pending")}
        print(f"{model}: known {counts['known']}, unknown {counts['unknown']}, pending {counts['pending']} "
              f"(of {len(rows)})")
    print(f"answers to check by hand: {sum(lab['check_by_hand'] == 'yes' and not lab['hand_label'] for lab in labels)}")


if __name__ == "__main__":
    main()
