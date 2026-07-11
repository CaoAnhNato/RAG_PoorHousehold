import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/Processed/cache/semantic_sql_cache.json', 'r', encoding='utf-8') as f:
    cache = json.load(f)

clean_cache = {}
removed = []
for k, v in cache.items():
    ans = str(v.get('answer', ''))
    sql = str(v.get('sql', '')).strip()
    
    # Check if answer indicates failure, no data found, or sql is invalid
    if ("Tôi không tìm thấy dữ liệu" in ans or 
        "Lỗi" in ans or 
        not sql or 
        "SELECT" not in sql.upper() or
        "đạt 100" in ans or
        "chưa có thông tin" in ans.lower() or
        "không thể xác định" in ans.lower()):
        removed.append(v.get('question'))
    else:
        clean_cache[k] = v

print(f"Removed {len(removed)} poisoned/bad cache entries out of {len(cache)}.")
with open('data/Processed/cache/semantic_sql_cache.json', 'w', encoding='utf-8') as f:
    json.dump(clean_cache, f, ensure_ascii=False, indent=2)
print("Saved cleaned cache successfully!")
