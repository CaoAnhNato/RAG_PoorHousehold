import duckdb
con = duckdb.connect()
res = con.execute("SELECT 1 AS a; SELECT 2 AS b;").df()
print("Result df shape:", res.shape)
print(res)
