#!/bin/bash
# List the public API of each version and compare them (candidate pool, Section 3.2.2).
# Uses the environments built by measurements/run_all.sh.
# Usage, from the repository root:  bash screening/run_api_diff.sh
set -e
cd "$(dirname "$0")/.."
ENVS=measurements/envs
for e in old mid new; do
  if [ ! -x "$ENVS/$e/bin/python" ]; then
    echo "missing $ENVS/$e: run 'bash measurements/run_all.sh' first"; exit 1
  fi
done
OUT=screening/results
mkdir -p "$OUT"

# pandas: 1.5.3 -> 2.2.3, both with NumPy 1.23.5
$ENVS/old/bin/python screening/api_dump.py pandas "$OUT/pandas_old.json"
$ENVS/mid/bin/python screening/api_dump.py pandas "$OUT/pandas_new.json" --probe "$OUT/pandas_old.json"
# NumPy: 1.23.5 -> 2.1.3, both with pandas 2.2.3
$ENVS/mid/bin/python screening/api_dump.py numpy "$OUT/numpy_old.json"
$ENVS/new/bin/python screening/api_dump.py numpy "$OUT/numpy_new.json" --probe "$OUT/numpy_old.json"

$ENVS/tools/bin/python screening/api_diff.py "$OUT/pandas_old.json" "$OUT/pandas_new.json" "$OUT/pandas_api_diff.csv"
$ENVS/tools/bin/python screening/api_diff.py "$OUT/numpy_old.json" "$OUT/numpy_new.json" "$OUT/numpy_api_diff.csv"
