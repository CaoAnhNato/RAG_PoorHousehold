import duckdb
import sys
sys.stdout.reconfigure(encoding='utf-8')
conn = duckdb.connect('data/Processed/intern_chatbot.duckdb')
schema = conn.execute("DESCRIBE households").df()
print("Columns in households:")
for _, row in schema.iterrows():
    print(row['column_name'], row['column_type'])

# Let's see some host names matching Tran Thi Lien
res = conn.execute("SELECT \"family.hostName\", \"family.ethnic\", \"administrative.district\" FROM households WHERE \"family.hostName\" LIKE '%Liên%' AND \"administrative.district\" LIKE '%Đắk Song%' LIMIT 5").df()
print("\nMatching Tran Thi Lien:")
print(res)
