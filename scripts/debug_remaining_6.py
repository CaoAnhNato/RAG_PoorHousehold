import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
from src.query_control.agentic.agent_pipeline import AgenticPipeline

target_ids = ['TC_048', 'TC_056', 'TC_061', 'TC_085', 'TC_088', 'TC_093']

with open('test/debug/100_qa_benchmark_results.json', 'r', encoding='utf-8') as f:
    results_data = json.load(f)

cases = {item['test_id']: item['prompt'] for item in results_data.get('detailed_results', []) if item['test_id'] in target_ids}

pipeline = AgenticPipeline()

for t_id, prompt in cases.items():
    print(f"\n=================== {t_id} ===================")
    print(f"Prompt: {prompt}")
    res = pipeline.process(prompt, mode="Hỏi - Đáp", stream=False)
    print(f"Error: {res.get('error')}")
    df = res.get('data')
    print(f"DF Type: {type(df)}")
    if isinstance(df, dict):
        for k, v in df.items():
            print(f"  {k}: shape {getattr(v, 'shape', None)}")
    else:
        print(f"DF Shape: {getattr(df, 'shape', None)}")
    print(f"SQL: {res.get('sql', 'N/A')}")
