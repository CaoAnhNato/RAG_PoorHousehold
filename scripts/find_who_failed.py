import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
from src.query_control.agentic.agent_pipeline import AgenticPipeline
import pandas as pd

with open('test/debug/100_qa_benchmark_results.json', 'r', encoding='utf-8') as f:
    results_data = json.load(f)

failed_ids = set()
for item in results_data.get('detailed_results', []):
    if not item.get('passed'):
        failed_ids.add(item.get('test_id'))

benchmark = results_data.get('test_cases', [])
if not benchmark:
    # If not in test_cases, build from detailed_results
    benchmark = results_data.get('detailed_results', [])

pipeline = AgenticPipeline()
final_failed = []
for tc in benchmark:
    if tc['test_id'] in failed_ids:
        out = pipeline.process(tc['prompt'], mode="Hỏi - Đáp", stream=False)
        df = out.get('data')
        if isinstance(df, pd.DataFrame):
            has_df = not df.empty
        elif isinstance(df, dict):
            has_df = any(isinstance(v, pd.DataFrame) and not v.empty for v in df.values())
        else:
            has_df = False
        has_text = bool(out.get('answer'))
        err = out.get('error')
        passed = has_df and has_text and not err
        if not passed:
            print(f"STILL FAILS IN RETEST: {tc['test_id']} | err={err} | df={has_df} | text={has_text}")
            final_failed.append(tc['test_id'])

print(f"\nFINAL FAILED LIST ({len(final_failed)}): {final_failed}")
