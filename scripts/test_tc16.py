import duckdb
import sys
sys.stdout.reconfigure(encoding='utf-8')

db = duckdb.connect('data/Processed/intern_chatbot.duckdb')

print("Tables:", db.execute("SHOW TABLES").fetchall())
print("Households columns with gender or host:", [c[0] for c in db.execute("DESCRIBE households").fetchall() if 'gender' in c[0].lower() or 'host' in c[0].lower()])
print("Members columns with gender:", [c[0] for c in db.execute("DESCRIBE members").fetchall() if 'gender' in c[0].lower()])

print("TC_016 SQL test:")
sql = """SELECT h."administrative.year" AS "Năm", COUNT(*) AS "Tổng số hộ nghèo có chủ hộ là nữ" 
FROM households h 
JOIN members m ON h."family.hostName" = m."member.fullName" AND h."administrative.year" = m."administrative.year"
WHERE h."classify" ILIKE '%Hộ nghèo%' 
  AND h."administrative.district" ILIKE '%Huyện Đắk Song%' 
  AND h."administrative.year" = 2024 
  AND m."member.gender" ILIKE '%Nữ%' 
GROUP BY h."administrative.year";"""
print(db.execute(sql).fetchall())
