from solution import caption_lines

out = caption_lines("A harbour at dusk, seen from the old lighthouse on the northern cliffs")
assert out == ["A harbour at dusk, seen", "from the old lighthouse", "on the northern cliffs"]
assert all(len(line) <= 24 for line in out)
print("PASS")
