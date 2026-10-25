"""Count the entries under "Removal of prior version deprecations/changes" in the pandas 2.0.0
release notes (Chapter 1 of the draft: 233).

Source: data/pandas_v2.0.0_whatsnew.rst, the source file doc/source/whatsnew/v2.0.0.rst of the
pandas repository (saved on Oct. 18, 2026). Each entry is a top-level bullet line starting with "- ".
Output: results/release_notes.json
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")


def main():
    text = open(os.path.join(ROOT, "data", "pandas_v2.0.0_whatsnew.rst"), encoding="utf-8").read()
    start = text.index(".. _whatsnew_200.prior_deprecations:")
    end = text.index(".. _whatsnew_200.performance:", start)
    entries = re.findall(r"^- ", text[start:end], re.M)
    out = dict(section="Removal of prior version deprecations/changes", entries=len(entries))
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "results", "release_notes.json"), "w"), indent=1)
    print(f"pandas 2.0.0 release notes, '{out['section']}': {out['entries']} entries")


if __name__ == "__main__":
    main()
