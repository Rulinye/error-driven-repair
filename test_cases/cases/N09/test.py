from solution import names_array

out = names_array(["Zoë", "Li"])
assert out.dtype.kind == "U"
assert out.tolist() == ["Zoë", "Li"]
print("PASS")
