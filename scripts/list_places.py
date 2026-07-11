import sys
sys.stdout.reconfigure(encoding='utf-8')
import duckdb
con = duckdb.connect("data/Processed/intern_chatbot.duckdb")

print("Districts:")
for d in con.execute("SELECT DISTINCT \"administrative.district\" FROM households").fetchall():
    print(" ", d[0])

print("\nCommunes:")
for c in sorted([x[0] for x in con.execute("SELECT DISTINCT \"administrative.commune\" FROM households").fetchall() if x[0]]):
    print(" ", c)
