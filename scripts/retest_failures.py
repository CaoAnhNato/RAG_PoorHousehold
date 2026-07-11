import json
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('.')

from src.query_control.agentic.agent_pipeline import AgenticPipeline

with open('test/debug/100_qa_benchmark_results.json', 'r', encoding='utf-8') as f:
    res = json.load(f)

failed_ids = [r['test_id'] for r in res['detailed_results'] if not r['passed']]

with open('test/comprehensive_100_qa_benchmark.json', 'r', encoding='utf-8') as f:
    benchmark = json.load(f)['test_cases']

pipeline = AgenticPipeline()

retest_passed = 0
for tc in benchmark:
    if tc['test_id'] in failed_ids:
        print(f"\nRe-testing {tc['test_id']}: {tc['prompt'][:60]}...")
        t0 = time.time()
        out = pipeline.process(tc['prompt'], mode="Hỏi - Đáp", stream=False)
        lat = time.time() - t0
        import pandas as pd
        df = out.get('data')
        if isinstance(df, pd.DataFrame):
            has_df = not df.empty
            shape = df.shape
        elif isinstance(df, dict):
            has_df = any(isinstance(v, pd.DataFrame) and not v.empty for v in df.values())
            shape = "Dict of DFs"
        else:
            has_df = False
            shape = "None"
        has_text = bool(out.get('answer'))
        err = out.get('error')
        passed = has_df and has_text and not err
        if passed:
            retest_passed += 1
            print(f"✅ NOW PASSED ({lat:.2f}s) | DF: {shape}")
        else:
            print(f"❌ STILL FAILED ({lat:.2f}s) | Error: {err} | DF: {has_df}")

print(f"\nRetest summary: {retest_passed}/{len(failed_ids)} now pass!")
