from solution import read_big_endian

assert read_big_endian(b"\x00\x01\x01\x00\x12\x34") == [1, 256, 0x1234]
print("PASS")
