"""Knowledge probe on the synthetic test cases (Sections 3.2.5 and 3.8).

usage: python synthetic/probe.py export REQUESTS.jsonl
       python synthetic/probe.py answers MODEL REPLIES.jsonl
       python synthetic/probe.py score

export writes one request per question of synthetic/results/questions.csv (synthetic/build.py), with the five
samples 0-4, in the format of `runs/run.py --export`; the prompt ids are probe-S01 to probe-S15, so the file can
be joined with other requests. answers takes the replies of a model to these prompts (other lines are left
out) into synthetic/results/answers.csv and keeps them in synthetic/results/probe/<MODEL>/. score labels every
answer with the rule of probe/README.md: the automatic match on the identifiers of the fix (SPEC in
synthetic/build.py), overridden by the hand labels in synthetic/results/hand_labels.csv (columns model, id,
sample, correct, reason). A synthetic test case is known to a model if at least three of its five answers are
correct; it is then treated like a known real change (Section 3.2.5). Writes answer_labels.csv and known.csv.
"""
import argparse
import csv
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
sys.path.insert(0, HERE)
from build import matches  # noqa: E402

SAMPLES = 5
KNOWN_AT = 3


def read(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def export(path):
    questions = read(os.path.join(RESULTS, "questions.csv"))
    with open(path, "w", encoding="utf-8") as out:
        for q in questions:
            out.write(json.dumps({"prompt_id": f"probe-{q['id']}", "case": q["id"], "text": q["question"],
                                  "samples": list(range(SAMPLES))}) + "\n")
    print(f"wrote {len(questions)} questions ({len(questions) * SAMPLES} samples) to {path}")


def answers(model, path):
    with open(path, encoding="utf-8") as f:
        replies = [r for r in map(json.loads, filter(str.strip, f)) if r["prompt_id"].startswith("probe-S")]
    folder = os.path.join(RESULTS, "probe", model)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "replies.jsonl"), "w", encoding="utf-8") as f:
        for r in replies:
            f.write(json.dumps(r) + "\n")
    if os.path.exists(path + ".meta.json"):
        shutil.copy(path + ".meta.json", os.path.join(folder, os.path.basename(path) + ".meta.json"))
    out_path = os.path.join(RESULTS, "answers.csv")
    rows = [r for r in read(out_path) if r["model"] != model]
    rows += [{"model": model, "id": r["case"], "sample": str(r["sample"]), "answer": r["text"]}
             for r in sorted(replies, key=lambda r: (r["case"], r["sample"]))]
    write(out_path, rows, ["model", "id", "sample", "answer"])
    print(f"{model}: {len(replies)} answers added to {out_path}")


def score():
    hand = {(h["model"], h["id"], h["sample"]): h for h in read(os.path.join(RESULTS, "hand_labels.csv"))}
    labels, known = [], []
    by_case = {}
    for a in read(os.path.join(RESULTS, "answers.csv")):
        auto = matches(a["id"], a["answer"])
        h = hand.get((a["model"], a["id"], a["sample"]))
        final = (h["correct"] == "yes") if h else auto
        labels.append({"model": a["model"], "id": a["id"], "sample": a["sample"], "automatic": "yes" if auto else "no",
                       "hand": h["correct"] if h else "", "correct": "yes" if final else "no",
                       "reason": h["reason"] if h else ""})
        by_case.setdefault((a["model"], a["id"]), []).append(final)
    for (model, cid), v in sorted(by_case.items()):
        assert len(v) == SAMPLES, (model, cid, len(v))
        known.append({"model": model, "id": cid, "correct": sum(v),
                      "label": "known" if sum(v) >= KNOWN_AT else "unknown"})
    write(os.path.join(RESULTS, "answer_labels.csv"), labels,
          ["model", "id", "sample", "automatic", "hand", "correct", "reason"])
    write(os.path.join(RESULTS, "known.csv"), known, ["model", "id", "correct", "label"])
    for model in sorted({k["model"] for k in known}):
        rows = [k for k in known if k["model"] == model]
        print(f"{model}: known {sum(k['label'] == 'known' for k in rows)} of {len(rows)}: "
              + " ".join(k["id"] for k in rows if k["label"] == "known"))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)
    e = sub.add_parser("export")
    e.add_argument("requests")
    a = sub.add_parser("answers")
    a.add_argument("model")
    a.add_argument("replies")
    sub.add_parser("score")
    args = ap.parse_args()
    if args.command == "export":
        export(args.requests)
    elif args.command == "answers":
        answers(args.model, args.replies)
    else:
        score()


if __name__ == "__main__":
    main()
