from solution import blur_tiles

heights = [[9, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0]]
assert blur_tiles(heights) == [[1.0, 1.0, 0.0, 1.0],
                               [1.0, 1.0, 0.0, 1.0],
                               [0.0, 0.0, 0.0, 0.0],
                               [1.0, 1.0, 0.0, 1.0]]
print("PASS")
