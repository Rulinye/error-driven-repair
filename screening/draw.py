"""Draw the changes added to the test cases (Section 3.2.2: at most 10, drawn at random if more qualify).

usage: python screening/draw.py
Reads results/pool.csv and writes results/draw.csv.

The draw is a simple random sample without replacement from the rows whose decision is
"meets criteria", taken in the order of their id, with a fixed seed so that it can be repeated.
"""
import csv
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SEED = 20261026
SIZE = 10


def main():
    with open(os.path.join(RESULTS, "pool.csv"), newline="", encoding="utf-8") as f:
        pool = list(csv.DictReader(f))
    eligible = sorted((r for r in pool if r["decision"] == "meets criteria"), key=lambda r: r["id"])
    drawn = sorted(random.Random(SEED).sample(eligible, min(SIZE, len(eligible))), key=lambda r: r["id"])
    path = os.path.join(RESULTS, "draw.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(pool[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(drawn)
    print(f"{len(drawn)} of {len(eligible)} rows that meet all criteria drawn with seed {SEED} -> {path}")
    for r in drawn:
        print(f"  {r['id']}  {r['change']}")


if __name__ == "__main__":
    main()
