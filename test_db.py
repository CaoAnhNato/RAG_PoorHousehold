import duckdb
import json

con = duckdb.connect('data/Processed/intern_chatbot.duckdb')
sql1 = """SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY district ORDER BY poor_household_count DESC"""
df = con.execute(sql1).df()
res_json = json.dumps(df.to_dict(orient='records'), indent=2, ensure_ascii=False)
with open('test_q1.json', 'w', encoding='utf-8') as f:
    f.write(res_json)
