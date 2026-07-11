import duckdb
con = duckdb.connect()
con.execute("CREATE TABLE members AS SELECT * FROM 'data/Processed/members.parquet'")
cols = con.execute("DESCRIBE members").fetchall()
for c in cols[:35]:
    print(c[0], "|", c[1])
