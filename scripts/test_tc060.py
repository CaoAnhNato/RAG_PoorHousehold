import duckdb
import sys
sys.stdout.reconfigure(encoding='utf-8')
db = duckdb.connect('data/Processed/intern_chatbot.duckdb')
res = db.execute("""SELECT "administrative.year" AS "Năm", SUM("family.numberOfMembers") AS "Số thành viên thoát nghèo"
FROM households
WHERE "transition.beginningClassify" = 'Hộ nghèo' AND "transition.endingClassify" = 'Hộ không nghèo' AND "administrative.year" = 2024
GROUP BY "administrative.year";""").df()
print(res)
