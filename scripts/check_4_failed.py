import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
from src.query_control.agentic.agent_pipeline import AgenticPipeline
import pandas as pd

with open('test/debug/100_qa_benchmark_results.json', 'r', encoding='utf-8') as f:
    results_data = json.load(f)

failed_cases = []
for item in results_data.get('detailed_results', []):
    if not item.get('passed'):
        failed_cases.append(item)

pipeline = AgenticPipeline()
for tc in failed_cases:
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
    if passed:
        print(f"✅ PASS: {tc['test_id']}")
    else:
        print(f"❌ FAIL: {tc['test_id']} | Err: {err} | DF: {has_df} | Ans: {bool(has_text)}")
