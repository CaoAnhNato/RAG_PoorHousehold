import duckdb
con = duckdb.connect("data/Processed/intern_chatbot.duckdb")
tables = con.execute("SHOW TABLES").fetchall()
print("Tables:", tables)
for t in tables:
    tname = t[0]
    cols = con.execute(f"DESCRIBE {tname}").fetchall()
    print(f"\nTable: {tname}")
    for c in cols:
        print(" ", c[0], "|", c[1])
