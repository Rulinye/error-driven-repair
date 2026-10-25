"""Small checks quoted in the draft:
  - the three library combinations run under Python 3.11 (Section 3.2.1)
  - a fix that calls the private DataFrame._append passes the pilot test (Sections 3.9, 5.4)
  - a fix that follows the E4 suggestion 'apply' fails the pilot test (Table 2)
  - typing a keyword-argument error and an import error under Python 3.11 gives no "Did you mean" (Section 5.4)
Output: results/extra.json
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
C1 = os.path.join(HERE, "..", "pilot_cases", "C1_pandas_append")
PATH_RE = re.compile(r"\(/[^)]*site-packages/[^)]*\)")


def versions(py):
    p = subprocess.run([py, "-c", "import sys, pandas as pd, numpy as np; df = pd.DataFrame({'a': [1, 2]}); "
                        "print(sys.version.split()[0], pd.__version__, np.__version__, int(df.a.sum()))"],
                       capture_output=True, text=True)
    parts = p.stdout.split()
    return dict(python=parts[0], pandas=parts[1], numpy=parts[2], runs=parts[3] == "3") if len(parts) == 4 else dict(error=p.stderr[-300:])


def c1_with(py, replacement):
    src = open(os.path.join(C1, "old.py")).read().replace("df.append(", replacement + "(")
    with tempfile.TemporaryDirectory() as tmp:
        open(os.path.join(tmp, "solution.py"), "w").write(src)
        shutil.copy(os.path.join(C1, "test.py"), os.path.join(tmp, "test.py"))
        p = subprocess.run([py, "-W", "ignore", "test.py"], cwd=tmp, capture_output=True, text=True)
        return p.returncode == 0 and "PASS" in p.stdout


def last_line(py, code):
    p = subprocess.run([py, "-c", code], capture_output=True, text=True)
    lines = [l for l in p.stderr.strip().splitlines() if l.strip()]
    return PATH_RE.sub("(<site-packages path>)", lines[-1]) if lines else "(no error)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env-old", required=True)
    ap.add_argument("--env-mid", required=True)
    ap.add_argument("--env-new", required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "..", "results", "extra.json"))
    a = ap.parse_args()
    a.env_old, a.env_mid, a.env_new = (os.path.abspath(x) for x in (a.env_old, a.env_mid, a.env_new))
    out = dict(
        envs={"old (pandas 1.5.3 + NumPy 1.23.5)": versions(a.env_old),
              "mid (pandas 2.2.3 + NumPy 1.23.5)": versions(a.env_mid),
              "new (pandas 2.2.3 + NumPy 2.1.3)": versions(a.env_new)},
        private_append_passes_test=c1_with(a.env_mid, "df._append"),
        e4_apply_passes_test=c1_with(a.env_mid, "df.apply"),
        keyword_error=last_line(a.env_mid, "import pandas as pd; pd.DataFrame({'a': [1]}).info(null_counts=True)"),
        import_error=last_line(a.env_mid, "from pandas.io.json import json_normalize"),
    )
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
