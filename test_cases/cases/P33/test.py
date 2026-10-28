from solution import read_headerless

out = read_headerless("1,x\n2,y\n")
assert list(out.columns) == ["col0", "col1"]
assert out["col0"].tolist() == [1, 2] and out["col1"].tolist() == ["x", "y"]
print("PASS")
