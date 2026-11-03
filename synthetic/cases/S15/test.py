from solution import reading_minutes

text = " ".join(["word"] * 450)
assert reading_minutes(text) == 2
assert reading_minutes(text, words_per_minute=100) == 4
assert reading_minutes("just a few words") == 1
print("PASS")
