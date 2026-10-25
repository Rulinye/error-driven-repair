"""Daily usage report, written in pandas 1.x style.

Reconstructs the usage report of a network-tool backend the author wrote with pandas
1.x; the original Python code was replaced when the backend was rewritten in Go.

usage: python v0.py <data_dir> <out_dir>
"""
import sys

import pandas as pd

data, out = sys.argv[1], sys.argv[2]

# --- 1. per-account usage from cumulative meters ----------------------------
r = pd.read_csv(f"{data}/meter_readings.csv", parse_dates=["ts"])
parts = r["meter"].str.split("/", expand=True)
r["device"] = parts[0]
r["direction"] = parts[1]
# an account can have several devices (acct01-a, acct01-b)
r["account"] = r["device"].str.replace(r"-[ab]$", "", regex=True)
r = r.sort_values(["node", "meter", "ts"])
r["delta"] = r.groupby(["node", "meter"])["value"].diff()
# a meter restarts from 0 after a node restart: the new value is the usage since then
r.loc[r["delta"] < 0, "delta"] = r["value"]
r["delta"] = r["delta"].fillna(0)

daily = r.groupby(["account", r["ts"].dt.date])["delta"].sum()
report = pd.DataFrame(columns=["account", "day", "bytes"])
for (acct, day), b in daily.items():
    report = pd.concat([report, pd.DataFrame([{"account": acct, "day": day, "bytes": b}])], ignore_index=True)

accounts = pd.read_csv(f"{data}/accounts.csv")
totals = report.groupby("account")["bytes"].sum().reset_index()
usage = accounts.merge(totals, on="account", how="left")
usage["used_after"] = usage["used_bytes"] + usage["bytes"].fillna(0)
usage["pct_quota"] = (usage["used_after"] / usage["quota_bytes"] * 100).round(1)

# --- 2. node summary ----------------------------------------------------------
nodes = pd.read_csv(f"{data}/nodes.csv")
m = pd.read_csv(f"{data}/node_metrics.csv", parse_dates=["ts"])
m = m.merge(nodes, on="node")
summary = m.groupby("node").mean(numeric_only=True)
summary["mem_pct"] = (summary["mem_used"] / summary["mem_total"] * 100).round(1)
peak = m.set_index("ts").groupby("node")["net_down_bps"].resample("1H").mean()
summary["peak_hour_down_bps"] = peak.groupby(level=0).max()

# --- 3. nodes per region --------------------------------------------------------
regions = nodes["region"].value_counts().rename_axis("region").reset_index(name="n_nodes")
regions = regions.sort_values(["n_nodes", "region"], ascending=[False, True])

# --- write (Unix line endings on every platform) --------------------------------
usage.to_csv(f"{out}/usage.csv", index=False, lineterminator="\n")
summary.round(1).to_csv(f"{out}/node_summary.csv", lineterminator="\n")
regions.to_csv(f"{out}/regions.csv", index=False, lineterminator="\n")
print(f"{len(report)} daily rows, {len(usage)} accounts, {len(summary)} nodes, {len(regions)} regions")
