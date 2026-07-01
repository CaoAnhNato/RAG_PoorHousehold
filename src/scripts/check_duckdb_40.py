import duckdb

conn = duckdb.connect('data/Processed/intern_chatbot.duckdb')
sql = '''SELECT CASE WHEN "deprivation.cleanWater" = true THEN 'Thiếu nước sinh hoạt' ELSE 'Đảm bảo nước sinh hoạt' END AS "Trạng thái nguồn nước", COUNT(*) AS "Số hộ nghèo" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Đắk Song%' AND "administrative.year" = 2024 
GROUP BY "deprivation.cleanWater"'''
res = conn.execute(sql).fetchall()
print("Result:", res)
