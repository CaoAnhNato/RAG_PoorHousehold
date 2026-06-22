import duckdb
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
conn = duckdb.connect('data/Processed/intern_chatbot.duckdb')

# Check classify unique values
res1 = conn.execute("SELECT DISTINCT classify FROM households").df()
print("Unique classify:", res1.to_dict(orient='records'))

# Check administrative.year unique values
res2 = conn.execute("SELECT DISTINCT \"administrative.year\" FROM households").df()
print("Unique year:", res2.to_dict(orient='records'))

# Check count by year
res3 = conn.execute("SELECT \"administrative.year\", COUNT(*) FROM households GROUP BY \"administrative.year\"").df()
print("Count by year:", res3.to_dict(orient='records'))

# Run Q1 query without WHERE classify='Hộ nghèo' just to see what comes out
res4 = conn.execute("SELECT \"administrative.district\" AS district, SUM(CASE WHEN \"classify\" LIKE '%nghèo%' THEN 1 ELSE 0 END) FROM households WHERE \"administrative.year\" = 2024 GROUP BY district").df()
print("Q1 without classify WHERE:", res4.to_dict(orient='records'))
