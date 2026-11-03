# One, two and three columns, and an empty field.
from solution import read_headerless

for text in ("1,x\n2,y\n", "5\n6\n", "1,2,3\n", "a,,c\n"):
    out = read_headerless(text)
    print(list(out.columns), out.values.tolist(), [str(d) for d in out.dtypes])
