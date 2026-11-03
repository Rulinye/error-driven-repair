from solution import brightest_after_clipping

image = [[10, 40, 260],
         [70, 15, 90],
         [5, 300, 20]]
assert brightest_after_clipping(image, 255) == (0, 2)
assert brightest_after_clipping(image, 400) == (2, 1)
print("PASS")
