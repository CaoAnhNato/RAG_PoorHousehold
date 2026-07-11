import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('.')

from src.query_control.agentic.sql_refiner import SQLRefiner

with open('test/debug/100_qa_benchmark_results.json', 'r', encoding='utf-8') as f:
    res = json.load(f)

failures = [r for r in res['detailed_results'] if not r['passed']]

refiner = SQLRefiner("data/Processed/intern_chatbot.duckdb")
for r in failures:
    print(f"=== {r['test_id']} ({r['category']}) ===")
    sql = r['sql']
    q = r['prompt']
    if not sql:
        print("No SQL generated.")
        continue
    try:
        df, refined = refiner.execute_and_refine(sql, q, {})
        if df is not None and not df.empty:
            print(f"✅ PASSED with shape: {df.shape}")
        else:
            print(f"❌ Returned empty DF.")
    except Exception as e:
        print(f"❌ Refiner Exception: {e}")
