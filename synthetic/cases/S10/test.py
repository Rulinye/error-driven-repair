from solution import wallpaper

assert wallpaper([[1, 2], [3, 4]], 2, 3) == [[1, 2, 1, 2, 1, 2], [3, 4, 3, 4, 3, 4],
                                            [1, 2, 1, 2, 1, 2], [3, 4, 3, 4, 3, 4]]
assert wallpaper([[7]], 1, 2) == [[7, 7]]
print("PASS")
