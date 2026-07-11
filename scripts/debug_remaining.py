import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('test/debug/100_qa_benchmark_results.json', 'r', encoding='utf-8') as f:
    res = json.load(f)

for r in res['detailed_results']:
    if r['test_id'] in ('TC_034', 'TC_036', 'TC_039', 'TC_048', 'TC_056', 'TC_060', 'TC_085', 'TC_092'):
        print(f"=== {r['test_id']} ===")
        print(f"Q: {r['prompt']}")
        print(f"SQL: {r['sql']}\n")
