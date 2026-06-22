import duckdb
import sys
sys.stdout.reconfigure(encoding='utf-8')
conn = duckdb.connect('data/Processed/intern_chatbot.duckdb')

queries = {
    13: """SELECT "administrative.commune" AS commune, COUNT(*) AS poor_count FROM households WHERE "administrative.district" = 'Huyện Cư Jút' AND "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY commune ORDER BY poor_count DESC""",
    14: """SELECT "administrative.village_or_group" AS village, COUNT(*) AS count FROM households WHERE "administrative.district" = 'Huyện Đắk Song' AND "administrative.year" = 2023 AND "classify" = 'Hộ nghèo' AND "family.hostGender" = 'Nữ' GROUP BY village ORDER BY count DESC LIMIT 1""",
    15: """SELECT "administrative.commune" AS commune, COUNT(*) AS lacking_clean_water_count FROM households WHERE "administrative.district" = 'Huyện Tuy Đức' AND "administrative.year" = 2024 AND "deprivation.cleanWater" = true GROUP BY commune ORDER BY lacking_clean_water_count DESC LIMIT 1""",
    16: """SELECT "family.ethnicity" AS ethnicity, b1Point AS b1_point, "family.isDTTS" AS is_dtts FROM households WHERE "family.hostName" LIKE '%Trần Thị Liên%' AND "administrative.district" = 'Huyện Đắk Song' LIMIT 1""",
    17: """SELECT COUNT(*) AS male_poor_host_count FROM households WHERE "administrative.district" = 'Huyện Đắk RLấp' AND "administrative.year" = 2023 AND "classify" = 'Hộ nghèo' AND "family.hostGender" = 'Nam'""",
    18: """SELECT "administrative.commune" AS commune, COUNT(*) AS poor_count FROM households WHERE "administrative.district" = 'Huyện Krông Nô' AND "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY commune ORDER BY poor_count DESC""",
    19: """SELECT "family.hostGender" AS gender, COUNT(*) AS count FROM households WHERE "administrative.district" = 'Huyện Tuy Đức' AND "administrative.year" = 2024 AND "classify" = 'Hộ nghèo' GROUP BY gender""",
    20: """SELECT "family.hostGender" AS gender, COUNT(*) AS count FROM households WHERE "administrative.district" = 'Huyện Tuy Đức' AND "administrative.year" = 2023 AND "family.isDTTS" = true GROUP BY gender"""
}

for q, sql in queries.items():
    print(f"--- Q{q} ---")
    try:
        print(conn.execute(sql).df().to_dict(orient='records'))
    except Exception as e:
        print("ERROR:", e)

