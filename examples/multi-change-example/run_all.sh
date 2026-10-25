#!/usr/bin/env bash
# Rerun the multi-change example and compare every result with expected/.
#
# usage: ./run_all.sh          configs old + new (the setup of the thesis)
#        ./run_all.sh all      also forced312 + forced313
#        ./run_all.sh record   maintainer only: run all configs and overwrite expected/
#
# Needs uv (https://docs.astral.sh/uv/), which also downloads the Python versions.
# Exit status: 0 if every check passes, 1 if any differs, 2 on setup errors.
set -u
cd "$(dirname "$0")"

MODE=${1:-check}
case "$MODE" in
  check) CONFIGS="old new" ;;
  all | record) CONFIGS="old new forced312 forced313" ;;
  *) echo "unknown mode: $MODE (use: check, all, record)"; exit 2 ;;
esac
STEPS="v0 v1 v2 v2_private_append v3 v4 v5 v5_private_append"

command -v uv >/dev/null || { echo "uv not found, see https://docs.astral.sh/uv/getting-started/installation/"; exit 2; }
if command -v sha256sum >/dev/null; then SHA="sha256sum"; else SHA="shasum -a 256"; fi

python_for() {
  case "$1" in
    old | new) echo 3.11.17 ;;
    forced312) echo 3.12.9 ;;
    forced313) echo 3.13.12 ;;
  esac
}

# last exception line (e.g. "KeyError: 'region'") or, on success, the last stdout line
outcome() {
  local dir=$1 rc=$2
  if [ "$rc" -eq 0 ]; then
    echo "exit=0 | $(tail -n 1 "$dir/stdout.txt")"
  else
    echo "exit=$rc | $(grep -E '^[A-Za-z_][A-Za-z0-9_.]*(Error|Exception): ' "$dir/stderr.txt" | tail -n 1 | cut -c1-200)"
  fi
}

rm -rf results && mkdir -p results .venvs

# --- environments -----------------------------------------------------------------
for cfg in $CONFIGS; do
  py=$(python_for "$cfg")
  echo "== setting up $cfg (Python $py)"
  rm -rf ".venvs/$cfg"
  uv venv -q --python "$py" ".venvs/$cfg" || exit 2
  uv pip install -q --python ".venvs/$cfg/bin/python" --require-hashes --only-binary :all: \
    -r "requirements/$cfg.txt" || exit 2
done

# --- data (identical for every config) ----------------------------------------------
first=${CONFIGS%% *}
".venvs/$first/bin/python" -I gen_data.py data >/dev/null || exit 2
(cd data && $SHA *.csv) > results/data.sha256

# --- run every step in every config -------------------------------------------------
for cfg in $CONFIGS; do
  mkdir -p "results/$cfg"
  ".venvs/$cfg/bin/python" -I -c "import sys, pandas, numpy; print('python', sys.version.split()[0]); print('pandas', pandas.__version__); print('numpy', numpy.__version__)" \
    > "results/$cfg/versions.txt"
  : > "results/$cfg/outcomes.txt"
  : > "results/$cfg/outputs.sha256"
  for step in $STEPS; do
    dir="results/$cfg/$step"
    mkdir -p "$dir/out"
    ".venvs/$cfg/bin/python" -I -W default "steps/$step.py" data "$dir/out" > "$dir/stdout.txt" 2> "$dir/stderr.txt"
    rc=$?
    printf '%s\t%s\n' "$step" "$(outcome "$dir" "$rc")" >> "results/$cfg/outcomes.txt"
    if [ "$rc" -eq 0 ]; then
      (cd "$dir/out" && $SHA *.csv | sed "s#  #  $step/#") >> "results/$cfg/outputs.sha256"
    fi
  done
done

# --- record or compare ----------------------------------------------------------------
if [ "$MODE" = record ]; then
  mkdir -p expected
  cp results/data.sha256 expected/data.sha256
  for cfg in $CONFIGS; do
    cp "results/$cfg/versions.txt" "expected/$cfg.versions.txt"
    cp "results/$cfg/outcomes.txt" "expected/$cfg.outcomes.txt"
    cp "results/$cfg/outputs.sha256" "expected/$cfg.outputs.sha256"
  done
  echo "expected/ overwritten"
  exit 0
fi

status=0
check() {  # check <label> <expected file> <actual file>
  if cmp -s "$2" "$3"; then
    echo "PASS  $1"
  else
    echo "FAIL  $1"
    diff "$2" "$3" | sed 's/^/      /' | cut -c1-200
    status=1
  fi
}

echo
check "input data" expected/data.sha256 results/data.sha256
for cfg in $CONFIGS; do
  echo
  echo "== $cfg: $(tr '\n' ' ' < "results/$cfg/versions.txt")"
  sed 's/^/   /' "results/$cfg/outcomes.txt" | cut -c1-140
  check "$cfg versions" "expected/$cfg.versions.txt" "results/$cfg/versions.txt"
  check "$cfg outcomes of all steps" "expected/$cfg.outcomes.txt" "results/$cfg/outcomes.txt"
  check "$cfg output files" "expected/$cfg.outputs.sha256" "results/$cfg/outputs.sha256"
done

# the fixed script under pandas 2.x writes the same files as the original under 1.5.3
echo
same_files() {  # same_files <label> <cfgA> <stepA> <cfgB> <stepB>
  a=$(grep " $3/" "results/$2/outputs.sha256" | sed "s# $3/# #")
  b=$(grep " $5/" "results/$4/outputs.sha256" | sed "s# $5/# #")
  if [ -n "$a" ] && [ "$a" = "$b" ]; then echo "PASS  $1"; else echo "FAIL  $1"; status=1; fi
}
for cfg in $CONFIGS; do
  [ "$cfg" = old ] && continue
  same_files "$cfg v5 output == old v0 output" "$cfg" v5 old v0
  same_files "$cfg v5_private_append output == $cfg v5 output" "$cfg" v5_private_append "$cfg" v5
done

echo
if [ "$status" -eq 0 ]; then echo "ALL CHECKS PASSED"; else echo "SOME CHECKS FAILED (see above)"; fi
exit "$status"
