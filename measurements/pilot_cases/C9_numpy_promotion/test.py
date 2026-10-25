from solution import add_offset
out = add_offset(16777216)
assert abs(float(out) - 16777216.1) < 0.01, f"precision lost: got {out!r}"
print("PASS")
