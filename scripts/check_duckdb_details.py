import duckdb
import sys
sys.stdout.reconfigure(encoding='utf-8')

db = duckdb.connect('data/Processed/intern_chatbot.duckdb')

print("1. Provinces & Districts in households:")
print(db.execute("SELECT DISTINCT \"administrative.province\", \"administrative.district\" FROM households LIMIT 10").fetchall())

print("2. TC_034 (Đắk Nông province vs district):")
print(db.execute("""SELECT COUNT(*) FROM households WHERE classify = 'Hộ nghèo' AND "deprivation.housingArea" = true AND "deprivation.housingQuality" = true AND "administrative.year" = 2024""").fetchall())

print("3. Columns with 'credit' or 'loan' or 'reason':")
print([c[0] for c in db.execute("DESCRIBE households").fetchall() if 'reason' in c[0].lower() or 'credit' in c[0].lower() or 'support' in c[0].lower()])

print("4. TC_039 check (adult education in Đăk Glong):")
print(db.execute("""SELECT COUNT(*) FROM households WHERE classify = 'Hộ nghèo' AND "family.isDTTS" = true AND "administrative.district" ILIKE '%Glong%' AND "administrative.year" = 2024""").fetchall())
print(db.execute("""SELECT COUNT(*) FROM households WHERE classify = 'Hộ nghèo' AND "family.isDTTS" = true AND "deprivation.adultEducation" = true AND "administrative.district" ILIKE '%Glong%' AND "administrative.year" = 2024""").fetchall())

print("5. TC_060 check transition classify distinct values:")
print(db.execute("SELECT DISTINCT \"transition.beginningClassify\", \"transition.endingClassify\" FROM households WHERE \"transition.beginningClassify\" IS NOT NULL LIMIT 10").fetchall())

print("6. TC_092 district spelling check:")
print(db.execute("SELECT DISTINCT \"administrative.district\" FROM households WHERE \"administrative.district\" ILIKE '%Lấp%'").fetchall())
