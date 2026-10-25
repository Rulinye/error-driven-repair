#!/bin/bash
# Reproduce every measured number in the thesis draft (Chapters 1, 3 and 5) on this computer.
# Usage (macOS or Linux):   bash run_all.sh
# Results: results/summary.md (table: draft number vs. local result), plus the raw results/*.json
set -e
cd "$(dirname "$0")"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed. Install it with:"
  echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
  echo "Then close Terminal, open it again, and run this script again."
  exit 1
fi

make_env () {
  name="$1"; shift
  if [ ! -x "envs/$name/bin/python" ]; then
    echo "== creating environment envs/$name (Python 3.11: $*)"
    uv venv --quiet --python 3.11 "envs/$name"
    uv pip install --quiet --python "envs/$name/bin/python" "$@"
  fi
}
make_env old   "pandas==1.5.3" "numpy==1.23.5"
make_env mid   "pandas==2.2.3" "numpy==1.23.5"
make_env new   "pandas==2.2.3" "numpy==2.1.3"
make_env tools "ruff==0.16.10"
make_env_py313 () {
  if [ ! -x "envs/py313/bin/python" ]; then
    echo "== creating environment envs/py313 (Python 3.13: pandas 2.2.3, NumPy 2.1.3)"
    uv venv --quiet --python 3.13 envs/py313
    uv pip install --quiet --python envs/py313/bin/python "pandas==2.2.3" "numpy==2.1.3"
  fi
}
make_env_py313

OLD=envs/old/bin/python; MID=envs/mid/bin/python; NEW=envs/new/bin/python; P313=envs/py313/bin/python; T=envs/tools/bin/python
mkdir -p results

echo; echo "== 1/8 pandas 2.0.0 release notes: count of removal entries (Chapter 1)"
$T scripts/count_release_notes.py
echo; echo "== 2/8 pilot: 9 cases (Chapter 5)"
$T scripts/pilot.py --env-old $OLD --env-mid $MID --env-new $NEW
echo; echo "== 3/8 Ruff on the pilot cases (Section 5.5)"
$T scripts/ruff_pilot.py --ruff envs/tools/bin/ruff --env-mid $MID --env-new $NEW
echo; echo "== 4/8 minimal calls of the 100 candidate changes (Section 3.2.2, takes a few minutes)"
$T scripts/candidates.py --env-old $OLD --env-mid $MID --env-new $NEW
echo; echo "== 5/8 interpreter suggestions for the 54 attribute errors (Section 5.4)"
$T scripts/probe_suggestions.py --env-mid $MID --env-new $NEW
echo; echo "== 6/8 small checks (environments, _append, E4 'apply')"
$T scripts/extra_checks.py --env-old $OLD --env-mid $MID --env-new $NEW > results/extra_checks.log
echo "saved results/extra.json"
echo; echo "== 7/8 the 82 error messages under Python 3.13 (Chapter 7)"
$T scripts/py313_messages.py --env-mid $MID --env-new $NEW --env-py313 $P313
echo; echo "== 8/8 comparison with the draft"
$T scripts/summarize.py
echo; echo "Done. Open results/summary.md"
