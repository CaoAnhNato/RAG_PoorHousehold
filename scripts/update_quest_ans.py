import sys
import duckdb
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

db_path = 'data/Processed/intern_chatbot.duckdb'
con = duckdb.connect(db_path)

# True correct SQL queries
questions = {
    1: """SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY district ORDER BY poor_household_count DESC""",
    2: """SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY district ORDER BY poor_household_count DESC LIMIT 1""",
    3: """SELECT SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_count, SUM(CASE WHEN "classify" = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS near_poor_count FROM households WHERE "administrative.year" = 2024""",
    4: """SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count, SUM(CASE WHEN "classify" = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS near_poor_household_count FROM households WHERE "administrative.year" = 2024 AND "classify" IN ('Hộ nghèo', 'Hộ cận nghèo') GROUP BY district ORDER BY poor_household_count DESC""",
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
    8: """SELECT SUM(CASE WHEN "classify" = 'Hộ nghèo' AND "deprivation.hygienicToilet" = 1 THEN 1 ELSE 0 END) AS poor_household_lacking_toilet FROM households WHERE "administrative.year" = 2023 AND "administrative.district" = 'Huyện Cư Jút'""",
    9: """SELECT "administrative.district" AS district,
  SUM(CASE WHEN "administrative.year" = 2023 THEN 1 ELSE 0 END) AS poor_household_count_2023,
  SUM(CASE WHEN "administrative.year" = 2024 THEN 1 ELSE 0 END) AS poor_household_count_2024,
  SUM(CASE WHEN "administrative.year" = 2024 THEN 1 ELSE 0 END) - SUM(CASE WHEN "administrative.year" = 2023 THEN 1 ELSE 0 END) AS diff_poor_household_count
FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.district" = 'Huyện Tuy Đức' AND "administrative.year" IN (2023, 2024)
GROUP BY district""",
    10: """SELECT "family.hostName" AS host_name, CAST("family.numberOfMembers" AS INTEGER) AS member_count FROM households WHERE "administrative.district" = 'Huyện Đắk Song' AND "administrative.year" = 2024 ORDER BY member_count DESC LIMIT 1""",
    11: """SELECT 
  SUM(CASE WHEN "deprivation.cleanWater" = 1 THEN 1 ELSE 0 END) AS cleanWater, 
  SUM(CASE WHEN "deprivation.hygienicToilet" = 1 THEN 1 ELSE 0 END) AS hygienicToilet, 
  SUM(CASE WHEN "reason.lackProductionLand" = 1 THEN 1 ELSE 0 END) AS lackProductionLand, 
  SUM(CASE WHEN "reason.lackCapital" = 1 THEN 1 ELSE 0 END) AS lackCapital, 
  SUM(CASE WHEN "reason.lackLabor" = 1 THEN 1 ELSE 0 END) AS lackLabor, 
  SUM(CASE WHEN "reason.illnessOrAccident" = 1 THEN 1 ELSE 0 END) AS illnessOrAccident 
FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.district" = 'Huyện Đắk Mil' AND "administrative.year" = 2024""",
    12: """SELECT 
  "administrative.district" AS district, 
  SUM(CASE WHEN "classify" = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS near_poor_count, 
  AVG(CASE WHEN "classify" = 'Hộ cận nghèo' THEN CAST("deprivation.totalCount" AS FLOAT) ELSE NULL END) AS avg_deprivation 
FROM households 
WHERE "classify" = 'Hộ cận nghèo' AND "administrative.year" = 2024 
GROUP BY district 
ORDER BY near_poor_count DESC, avg_deprivation ASC 
LIMIT 1""",
    13: """SELECT "administrative.commune" AS commune, COUNT(*) AS poor_count FROM households WHERE "administrative.district" = 'Huyện Cư Jút' AND "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY commune ORDER BY poor_count DESC""",
    14: """SELECT "administrative.village_or_group" AS village, COUNT(*) AS count FROM households WHERE "administrative.district" = 'Huyện Đắk Song' AND "administrative.year" = 2023 AND "classify" = 'Hộ nghèo' AND "family.hostGender" = 'Nữ' GROUP BY village ORDER BY count DESC LIMIT 1""",
    15: """SELECT "administrative.commune" AS commune, COUNT(*) AS lacking_clean_water_count FROM households WHERE "administrative.district" = 'Huyện Tuy Đức' AND "administrative.year" = 2024 AND "deprivation.cleanWater" = true GROUP BY commune ORDER BY lacking_clean_water_count DESC LIMIT 1""",
    16: """SELECT "family.ethnicity" AS ethnicity, b1Point AS b1_point, "family.isDTTS" AS is_dtts FROM households WHERE "family.hostName" LIKE '%Trần Thị Liên%' AND "administrative.district" = 'Huyện Đắk Song' LIMIT 1""",
    17: """SELECT COUNT(*) AS male_poor_host_count FROM households WHERE "administrative.district" = 'Huyện Đắk RLấp' AND "administrative.year" = 2023 AND "classify" = 'Hộ nghèo' AND "family.hostGender" = 'Nam'""",
    18: """SELECT "administrative.commune" AS commune, COUNT(*) AS poor_count FROM households WHERE "administrative.district" = 'Huyện Krông Nô' AND "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY commune ORDER BY poor_count DESC""",
    19: """SELECT "family.hostGender" AS gender, COUNT(*) AS count FROM households WHERE "administrative.district" = 'Huyện Tuy Đức' AND "administrative.year" = 2024 AND "classify" = 'Hộ nghèo' GROUP BY gender""",
    20: """SELECT "family.hostGender" AS gender, COUNT(*) AS count FROM households WHERE "administrative.district" = 'Huyện Tuy Đức' AND "administrative.year" = 2023 AND "family.isDTTS" = true GROUP BY gender"""
}

file_path = 'artifacts/quest_ans.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content_blocks = re.split(r'\n---\n', content)

for q_num, sql in questions.items():
    # Execute SQL
    try:
        df = con.execute(sql).df()
        res_json = json.dumps(df.to_dict(orient='records'), indent=2, ensure_ascii=False)
    except Exception as e:
        res_json = f"[\n  {json.dumps(str(e))}\n]"
    
    # Process blocks
    for i, block in enumerate(content_blocks):
        if re.search(rf"^## {q_num}\. ", block.strip(), flags=re.MULTILINE):
            block = re.sub(r"(### Lệnh SQL\s*```sql\s*).*?(\s*```)", rf"\g<1>{sql}\g<2>", block, flags=re.DOTALL)
            block = re.sub(r"(### Dữ liệu trả về từ DB\s*```json\s*).*?(\s*```)", rf"\g<1>{res_json}\g<2>", block, flags=re.DOTALL)
            content_blocks[i] = block

with open(file_path, 'w', encoding='utf-8') as f:
    f.write('\n\n---\n\n'.join(content_blocks))

print("Updated artifacts/quest_ans.md successfully!")
