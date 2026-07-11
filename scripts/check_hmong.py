import sys
sys.stdout.reconfigure(encoding='utf-8')
import duckdb
con = duckdb.connect("data/Processed/intern_chatbot.duckdb")

print("Members ethnicity in Xã Quảng Hoà (Hộ nghèo):")
print(con.execute("""
SELECT m."member.ethnicity", COUNT(*)
FROM members m
JOIN households h ON m."administrative.district" = h."administrative.district"
  AND m."administrative.commune" = h."administrative.commune"
  AND m."family.hostName" = h."family.hostName"
  AND m."administrative.year" = h."administrative.year"
WHERE h.classify = 'Hộ nghèo' AND h."administrative.commune" = 'Xã Quảng Hoà' AND h."administrative.year" = 2024
GROUP BY m."member.ethnicity"
""").fetchall())
