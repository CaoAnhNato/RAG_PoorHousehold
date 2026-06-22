import sys
sys.stdout.reconfigure(encoding='utf-8')
import duckdb
import json

db_path = 'data/Processed/intern_chatbot.duckdb'
con = duckdb.connect(db_path)

questions = {
    1: """SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY district ORDER BY poor_household_count DESC""",
    2: """SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY district ORDER BY poor_household_count DESC LIMIT 1""",
    4: """SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count, SUM(CASE WHEN "classify" = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS near_poor_household_count FROM households WHERE "administrative.year" = 2024 AND LOWER("classify") IN ('hộ nghèo', 'hộ cận nghèo') GROUP BY district ORDER BY poor_household_count DESC""",
    5: """SELECT "administrative.district" AS district,
  SUM(CASE WHEN "administrative.year" = 2023 THEN 1 ELSE 0 END) AS poor_household_count_2023,
  SUM(CASE WHEN "administrative.year" = 2024 THEN 1 ELSE 0 END) AS poor_household_count_2024,
  SUM(CASE WHEN "administrative.year" = 2024 THEN 1 ELSE 0 END) - SUM(CASE WHEN "administrative.year" = 2023 THEN 1 ELSE 0 END) AS diff_poor_household_count
FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.district" = 'Thành phố Gia Nghĩa' AND "administrative.year" IN (2023, 2024)
GROUP BY district""",
    6: """SELECT "administrative.district" AS district,
  SUM(CASE WHEN "administrative.year" = 2023 THEN 1 ELSE 0 END) AS poor_household_count_2023,
  SUM(CASE WHEN "administrative.year" = 2024 THEN 1 ELSE 0 END) AS poor_household_count_2024,
  SUM(CASE WHEN "administrative.year" = 2024 THEN 1 ELSE 0 END) - SUM(CASE WHEN "administrative.year" = 2023 THEN 1 ELSE 0 END) AS diff_poor_household_count
FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.district" = 'Huyện Đắk Song' AND "administrative.year" IN (2023, 2024)
GROUP BY district""",
    7: """SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS near_poor_household_count FROM households WHERE "classify" = 'Hộ cận nghèo' AND "administrative.year" = 2024 GROUP BY district ORDER BY near_poor_household_count DESC LIMIT 1""",
    8: """SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 AND "administrative.district" = 'Huyện Cư Jút' AND "deprivation.hygienicToilet" = 1 GROUP BY district""",
    9: """SELECT "administrative.district" AS district,
  SUM(CASE WHEN "administrative.year" = 2023 THEN 1 ELSE 0 END) AS poor_household_count_2023,
  SUM(CASE WHEN "administrative.year" = 2024 THEN 1 ELSE 0 END) AS poor_household_count_2024,
  SUM(CASE WHEN "administrative.year" = 2024 THEN 1 ELSE 0 END) - SUM(CASE WHEN "administrative.year" = 2023 THEN 1 ELSE 0 END) AS diff_poor_household_count
FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.district" = 'Huyện Tuy Đức' AND "administrative.year" IN (2023, 2024)
GROUP BY district""",
    10: """SELECT "family.hostName" AS host_name, CAST("family.memberCount" AS INTEGER) AS member_count FROM households WHERE "administrative.district" = 'Huyện Đắk Song' AND "administrative.year" = 2024 ORDER BY member_count DESC LIMIT 1""",
    11: """SELECT "deprivation.cleanWater" AS cleanWater, "deprivation.hygienicToilet" AS hygienicToilet, "reason.lackProductionLand" AS lackProductionLand, "reason.lackCapital" AS lackCapital, "reason.lackLabor" AS lackLabor, "reason.illnessOrAccident" AS illnessOrAccident FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.district" = 'Huyện Đắk Mil' AND "administrative.year" = 2024"""
}

res = {}
for q, sql in questions.items():
    try:
        df = con.execute(sql).df()
        res[q] = df.to_dict(orient='records')
    except Exception as e:
        res[q] = str(e)
        
print(json.dumps(res, indent=2, ensure_ascii=False))
