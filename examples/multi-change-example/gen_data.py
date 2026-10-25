"""Generate the synthetic input data for the multi-change example.

Standard library only and seeded, so every Python 3 version writes identical files.

usage: python gen_data.py <out_dir>

Files:
  meter_readings.csv  cumulative usage meters, one reading per meter every 5 minutes;
                      a meter restarts from 0 when its node restarts
  accounts.csv        accounts with a quota and the usage already counted
  nodes.csv           nodes with a display name, a region and a monthly plan
  node_metrics.csv    resource samples per node every 5 minutes
"""
import csv
import os
import random
import sys
from datetime import datetime, timedelta

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
rng = random.Random(20261025)

NODES = ["node1", "node2", "node3", "node4", "node5", "node6"]
REGIONS = {"node1": "region-a", "node2": "region-b", "node3": "region-c",
           "node4": "region-d", "node5": "region-e", "node6": "region-a"}
ACCOUNTS = [f"acct{i:02d}" for i in range(1, 13)]
START = datetime(2026, 10, 1, 0, 0, 0)
STEP = timedelta(minutes=5)
N_STEPS = 3 * 24 * 12  # 3 days of 5-minute readings

# --- meter readings (cumulative per node/meter, with occasional restarts) ---
with open(f"{out}/meter_readings.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ts", "node", "meter", "value"])
    for node in NODES:
        for acct in ACCOUNTS:
            if rng.random() < 0.55:
                continue
            for device in ["a", "b"]:
                if device == "b" and rng.random() < 0.5:
                    continue
                for direction in ["tx", "rx"]:
                    meter = f"{acct}-{device}/{direction}"
                    rate = rng.uniform(2e4, 4e5) * (8 if direction == "rx" else 1)
                    value = 0
                    for i in range(N_STEPS):
                        if rng.random() < 0.002:  # node restart resets the meter
                            value = 0
                        value += int(rate * 300 * rng.uniform(0, 2) * (rng.random() < 0.7))
                        w.writerow([(START + i * STEP).strftime("%Y-%m-%d %H:%M:%S"), node, meter, value])

# --- accounts ---
with open(f"{out}/accounts.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["account", "quota_bytes", "used_bytes"])
    for acct in ACCOUNTS:
        quota = "" if rng.random() < 0.2 else 100 * 1024**3
        w.writerow([acct, quota, rng.randint(0, 40) * 1024**3])

# --- nodes ---
with open(f"{out}/nodes.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["node", "display_name", "region", "monthly_limit_bytes", "metering"])
    for n in NODES:
        w.writerow([n, n.upper(), REGIONS[n], rng.choice([1024**4, 2 * 1024**4, ""]), rng.choice(["both", "max"])])

# --- node metrics ---
with open(f"{out}/node_metrics.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["node", "ts", "cpu_pct", "mem_used", "mem_total", "net_up_bps", "net_down_bps", "load1", "tcp_conn"])
    for n in NODES:
        mem_total = rng.choice([1, 2, 4]) * 1024**3
        for i in range(N_STEPS):
            w.writerow([
                n,
                (START + i * STEP).strftime("%Y-%m-%d %H:%M:%S"),
                round(rng.uniform(1, 60), 1),
                int(mem_total * rng.uniform(0.3, 0.8)),
                mem_total,
                rng.randint(10_000, 5_000_000),
                rng.randint(100_000, 40_000_000),
                round(rng.uniform(0, 2), 2),
                rng.randint(5, 400),
            ])

print("written to", out)
