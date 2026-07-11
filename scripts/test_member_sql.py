import sys
sys.stdout.reconfigure(encoding='utf-8')
from src.query_control.agentic.agent_pipeline import AgenticPipeline

prompts = {
    'TC_048': "Xã Quảng Hòa (Đăk Glong) có bao nhiêu thành viên là dân tộc Mông thuộc các hộ nghèo năm 2024?",
    'TC_056': "Xã Nam Dong (Huyện Cư Jút) có bao nhiêu thành viên hộ nghèo sinh từ năm 2015 đến nay (dưới 10 tuổi) năm 2024?"
}

pipeline = AgenticPipeline()
for tid, prompt in prompts.items():
    print(f"\n=================== {tid} ===================")
    res = pipeline.process(prompt, mode="Hỏi - Đáp", stream=False)
    print("SQL:\n", res.get('sql'))
    print("Error:", res.get('error'))
    df = res.get('data')
    if df is not None:
        print("Result DF:\n", df)
