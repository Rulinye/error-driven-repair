"""Requests and answers of the knowledge probe, for the notebooks of runs/open_models and runs/api_models.

usage: python probe/requests.py export REQUESTS.jsonl
       python probe/requests.py answers MODEL REPLIES.jsonl

export writes one request per question of probe/results/questions.csv, with the five samples 0-4, in the
format of `runs/run.py --export`; the question is the whole prompt (Section 3.8). The notebooks sample it at
the temperature and with the settings of the main runs.

answers adds the replies of a model to probe/results/answers.csv (columns model, id, sample, answer, the input
of probe/score.py) and keeps the replies, with their tokens and cost, and the notebook's .meta.json in
probe/results/<MODEL>/. Answers of the model already in answers.csv are replaced.
"""
import argparse
import csv
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SAMPLES = 5


def export(path):
    with open(os.path.join(RESULTS, "questions.csv"), encoding="utf-8") as f:
        questions = list(csv.DictReader(f))
    with open(path, "w", encoding="utf-8") as out:
        for q in questions:
            out.write(json.dumps({"prompt_id": f"probe-{q['id']}", "case": q["id"], "text": q["question"],
                                  "samples": list(range(SAMPLES))}) + "\n")
    print(f"wrote {len(questions)} questions ({len(questions) * SAMPLES} samples) to {path}")


def answers(model, path):
    with open(path, encoding="utf-8") as f:
        replies = [json.loads(line) for line in f if line.strip()]
    folder = os.path.join(RESULTS, model)
    os.makedirs(folder, exist_ok=True)
    shutil.copy(path, os.path.join(folder, "replies.jsonl"))
    if os.path.exists(path + ".meta.json"):
        shutil.copy(path + ".meta.json", os.path.join(folder, os.path.basename(path) + ".meta.json"))
    out_path = os.path.join(RESULTS, "answers.csv")
    rows = []
    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r["model"] != model]
    rows += [{"model": model, "id": r["case"], "sample": str(r["sample"]), "answer": r["text"]}
             for r in sorted(replies, key=lambda r: (r["case"][0] == "N", r["case"], r["sample"]))]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["model", "id", "sample", "answer"])
        w.writeheader()
        w.writerows(rows)
    print(f"{model}: {len(replies)} answers added to {out_path}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)
    e = sub.add_parser("export")
    e.add_argument("requests")
    a = sub.add_parser("answers")
    a.add_argument("model")
    a.add_argument("replies")
    args = ap.parse_args()
    if args.command == "export":
        export(args.requests)
    else:
        answers(args.model, args.replies)


if __name__ == "__main__":
    main()
