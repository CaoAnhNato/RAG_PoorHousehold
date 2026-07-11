import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/Processed/cache/semantic_sql_cache.json', 'r', encoding='utf-8') as f:
    cache = json.load(f)

bad_count = 0
for k, v in cache.items():
    ans = str(v.get('answer', ''))
    sql = str(v.get('sql', '')).strip()
    if "Tôi không tìm thấy dữ liệu" in ans or "Lỗi" in ans or not sql or "đạt 100" in ans or "SELECT" not in sql.upper():
        bad_count += 1
        if bad_count <= 10:
            print(f"[{k}] Q: {v.get('question')}")
            print(f"  SQL: {sql[:100]}...")
            print(f"  Ans: {ans[:100]}...\n")

print(f"Total bad cache entries detected: {bad_count}/{len(cache)}")
