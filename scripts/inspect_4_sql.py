import sys
sys.stdout.reconfigure(encoding='utf-8')
from src.query_control.agentic.agent_pipeline import AgenticPipeline

prompts = {
    'TC_048': "Xã Quảng Hòa (Đăk Glong) có bao nhiêu thành viên là dân tộc Mông thuộc các hộ nghèo năm 2024?",
    'TC_056': "Xã Nam Dong (Huyện Cư Jút) có bao nhiêu thành viên hộ nghèo sinh từ năm 2015 đến nay (dưới 10 tuổi) năm 2024?",
    'TC_061': "Hãy thống kê tổng số hộ nghèo tại Đắk Mil năm 2024, tính tỷ lệ hộ nghèo là người DTTS tại huyện này, và cho biết xã nào ở Đắk Mil có số hộ nghèo đông nhất.",
    'TC_085': "Báo cáo thực trạng đồng bào DTTS tại Đăk Glong 2024: Bảng 1: Thống kê hộ nghèo DTTS theo các xã; Bảng 2: Cơ cấu dân tộc (Mông, M'Nông, Dao...) của thành viên trong hộ nghèo."
}

pipeline = AgenticPipeline()
for tid, prompt in prompts.items():
    print(f"\n=================== {tid} ===================")
    res = pipeline.process(prompt, mode="Hỏi - Đáp", stream=False)
    print("SQL:\n", res.get('sql'))
