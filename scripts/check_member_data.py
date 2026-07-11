import sys
sys.stdout.reconfigure(encoding='utf-8')
import duckdb
con = duckdb.connect("data/Processed/intern_chatbot.duckdb")

print("Communes in Đăk Glong:")
print(con.execute("SELECT DISTINCT \"administrative.commune\" FROM households WHERE \"administrative.district\" ILIKE '%Glong%'").fetchall())
