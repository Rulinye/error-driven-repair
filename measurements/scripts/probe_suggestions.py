"""Interpreter "Did you mean" suggestions for the attribute errors (Section 5.4).

Each removed attribute is accessed in a fresh Python 3.11 process and the exception is left
uncaught, because Python 3.11 adds its suggestion only when it prints an uncaught exception.
NumPy attributes run with NumPy 2.1.3; pandas attributes with pandas 2.2.3 (+ NumPy 1.23.5).
Output: results/suggestions.json
"""
import argparse
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SETUP = """
import numpy as np, pandas as pd
df = pd.DataFrame({'a':[1,2],'b':[3,4]}); s = pd.Series([1.0,2.0,3.0])
idx = pd.Index([1,2,3]); dti = pd.date_range('2020-01-01', periods=3); sdt = pd.Series(dti)
cat = pd.Categorical(['a','b','a']); arr = np.array([1,2,3]); g = df.groupby('a')
"""
# the 54 attribute errors among the 82 erroring changes (IDs as in data/changes.csv)
CASES = {
    'N01': 'np.float', 'N02': 'np.int', 'N04': 'np.object', 'N05': 'np.str', 'N06': 'np.float_', 'N07': 'np.complex_',
    'N08': 'np.string_', 'N09': 'np.unicode_', 'N10': 'np.NaN', 'N11': 'np.Inf', 'N12': 'np.infty', 'N13': 'np.NINF',
    'N14': 'np.product', 'N15': 'np.cumproduct', 'N16': 'np.alltrue', 'N17': 'np.sometrue', 'N18': 'np.round_',
    'N19': 'np.asfarray', 'N20': 'np.cast', 'N21': 'np.mat', 'N22': 'np.find_common_type', 'N26': 'np.longfloat',
    'N27': 'np.cfloat', 'N37': 'np.AxisError', 'N38': 'np.VisibleDeprecationWarning', 'N32': 'arr.ptp',
    'N23': 'np.issubsctype', 'N24': 'np.issubclass_', 'N28': 'np.obj2sctype', 'N29': 'np.sctype2char', 'N30': 'np.nbytes',
    'N31': 'np.fastCopyAndTranspose', 'N33': 'arr.newbyteorder',
    'P01': 'df.append', 'P02': 's.append', 'P03': 'df.iteritems', 'P04': 's.iteritems', 'P05': 'pd.Int64Index',
    'P06': 'pd.Float64Index', 'P07': 'pd.UInt64Index', 'P09': 'idx.is_monotonic', 'P10': 's.is_monotonic',
    'P11': 'dti.week', 'P12': 'sdt.dt.week', 'P13': 'cat.to_dense', 'P14': 'cat.mode', 'P18': 'dti.to_perioddelta',
    'P26': 's.mad', 'P27': 'df.mad', 'P28': 's.tshift', 'P44': 'g.pad', 'P54': 'dti.union_many',
    'P15': 'idx.to_native_types', 'P16': 'idx.is_mixed',
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env-mid", required=True, help="pandas 2.2.3 + NumPy 1.23.5")
    ap.add_argument("--env-new", required=True, help="pandas 2.2.3 + NumPy 2.1.3")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "results", "suggestions.json"))
    a = ap.parse_args()
    out = {}
    for cid, expr in CASES.items():
        py = a.env_new if cid.startswith("N") else a.env_mid
        p = subprocess.run([py, "-c", SETUP + f"\n{expr}\n"], capture_output=True, text=True, timeout=120)
        lines = [l for l in p.stderr.strip().splitlines() if l.strip()]
        start = max([i for i, l in enumerate(lines) if l.startswith("AttributeError")] or [len(lines) - 1])
        msg = " ".join(l.strip() for l in lines[start:]) if lines else "(no error)"
        sugg = msg.split("Did you mean: ")[1].strip(" ?'") if "Did you mean: " in msg else None
        out[cid] = dict(expr=expr, message=msg, suggestion=sugg)
        if sugg:
            print(f"{cid}: {expr} -> Did you mean '{sugg}'")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)
    n = sum(1 for v in out.values() if v["suggestion"])
    print(f"{len(out)} attribute errors, {n} with a suggestion -> {os.path.abspath(a.out)}")


if __name__ == "__main__":
    main()
