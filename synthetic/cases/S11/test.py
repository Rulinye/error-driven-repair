from solution import article_url

assert article_url("Café Society: Notes & Queries", 42) == "/articles/42-cafe-society-notes-queries"
assert article_url("  Ten   Years On ", 7) == "/articles/7-ten-years-on"
print("PASS")
