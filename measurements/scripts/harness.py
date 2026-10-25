"""Run one code snippet inside a given Python environment and print a JSON result.

Called by candidates.py with the environment's own Python, e.g.
    envs/old/bin/python scripts/harness.py < snippet.json

The snippet sets a variable named `result`. The harness prints either
    {"status": "ok", "result": <normalized value>, "warnings": [...]}
or
    {"status": "error", "exc": "<type>", "message": "<full library message>", "warnings": [...]}
The message is the exception text WITHOUT any interpreter "Did you mean" suggestion
(Python 3.11 adds those only when it prints an uncaught exception).
"""
import json
import math
import sys
import traceback
import warnings


def norm(x, full=False, depth=0):
    import numpy as np
    import pandas as pd
    if depth > 6:
        return repr(x)
    if x is None or isinstance(x, (bool, str)):
        return x
    if isinstance(x, int):
        return x
    if isinstance(x, float):
        if math.isnan(x):
            return "nan"
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        if x.is_integer():
            return int(x)
        return float(f"{x:.10g}")
    if isinstance(x, type):
        try:
            return {"dtype": np.dtype(x).name}
        except Exception:
            return {"type": x.__name__}
    if isinstance(x, np.dtype):
        return {"dtype": str(x)}
    if isinstance(x, (pd.Timestamp, np.datetime64)):
        return "T:" + str(pd.Timestamp(x))
    if isinstance(x, (pd.Timedelta, np.timedelta64)):
        return "TD:" + str(pd.Timedelta(x))
    if isinstance(x, np.generic):
        return norm(x.item(), full, depth + 1)
    if isinstance(x, pd.DataFrame):
        return {"columns": [str(c) for c in x.columns],
                "index": [norm(i, False, depth + 1) for i in x.index],
                "data": [[norm(v, False, depth + 1) for v in row] for row in x.itertuples(index=False)]}
    if isinstance(x, pd.Series) and full:
        return {"values": [norm(v, False, depth + 1) for v in x.tolist()],
                "index": [norm(i, False, depth + 1) for i in x.index]}
    if isinstance(x, (pd.Series, pd.Index)):
        return [norm(v, False, depth + 1) for v in x.tolist()]
    if isinstance(x, pd.Categorical):
        return [norm(v, False, depth + 1) for v in np.asarray(x, dtype=object).tolist()]
    if isinstance(x, np.ndarray):
        return norm(x.tolist(), full, depth + 1)
    if isinstance(x, (list, tuple)):
        return [norm(v, full, depth + 1) for v in x]
    if isinstance(x, dict):
        return {str(k): norm(v, full, depth + 1) for k, v in x.items()}
    return repr(x)


def main():
    spec = json.load(sys.stdin)
    ns = {}
    caught = []
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            exec(compile(spec["code"], "<snippet>", "exec"), ns)
            out = {"status": "ok", "result": norm(ns.get("result"), spec.get("mode") == "full")}
        except BaseException as e:  # noqa: BLE001 - we want every failure recorded
            msg = "".join(traceback.format_exception_only(type(e), e)).strip()
            out = {"status": "error", "exc": type(e).__name__, "message": msg}
        for item in w:
            if issubclass(item.category, (FutureWarning, DeprecationWarning)):
                text = " ".join(str(item.message).split())
                if text not in caught:
                    caught.append(text)
    out["warnings"] = caught
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
