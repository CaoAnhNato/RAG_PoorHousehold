import duckdb
import sys
sys.stdout.reconfigure(encoding='utf-8')
conn = duckdb.connect('data/Processed/intern_chatbot.duckdb')
q1 = """
SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY district ORDER BY poor_household_count DESC
"""
print(conn.execute(q1).df())
