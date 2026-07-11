import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/Processed/cache/semantic_sql_cache.json', 'r', encoding='utf-8') as f:
    cache = json.load(f)

for k in ('e2e1c32d93e9a335468ba3d51c27bfde', '8b1ce92c06a5a891e2ea7961fc2bf91c'):
    if k in cache:
        print(f"Key: {k}")
        print(f"Q: {cache[k].get('question')}")
        print(f"SQL: {cache[k].get('sql')}\n")
