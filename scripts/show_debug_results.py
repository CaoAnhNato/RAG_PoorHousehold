import sys
sys.stdout.reconfigure(encoding='utf-8')
from src.query_control.agentic.agent_pipeline import AgenticPipeline
import pandas as pd

target_ids = ['TC_048', 'TC_056', 'TC_061', 'TC_085', 'TC_088', 'TC_093']
prompts = {
    'TC_048': "Xã Quảng Hòa (Đăk Glong) có bao nhiêu thành viên là dân tộc Mông thuộc các hộ nghèo năm 2024?",
    'TC_056': "Xã Nam Dong (Huyện Cư Jút) có bao nhiêu thành viên hộ nghèo sinh từ năm 2015 đến nay (dưới 10 tuổi) năm 2024?",
    'TC_061': "Hãy thống kê tổng số hộ nghèo tại Đắk Mil năm 2024, tính tỷ lệ hộ nghèo là người DTTS tại huyện này, và cho biết xã nào ở Đắk Mil có số hộ nghèo đông nhất.",
    'TC_085': "Báo cáo thực trạng đồng bào DTTS tại Đăk Glong 2024: Bảng 1: Thống kê hộ nghèo DTTS theo các xã; Bảng 2: Cơ cấu dân tộc (Mông, M'Nông, Dao...) của thành viên trong hộ nghèo.",
    'TC_088': "Thống kê tình trạng hộ cận nghèo TP. Gia Nghĩa năm 2024 qua 2 bảng: Bảng 1: Phân bố hộ cận nghèo theo phường/xã; Bảng 2: Phân loại theo giới tính và độ tuổi trung bình chủ hộ.",
    'TC_093': "Báo cáo tổng kết bảo hiểm y tế toàn tỉnh 2024: Bảng 1: Tỷ lệ BHYT cấp hộ gia đình theo huyện; Bảng 2: Tỷ lệ BHYT cấp thành viên theo huyện."
}

pipeline = AgenticPipeline()
for tid, prompt in prompts.items():
    print(f"\n--- Checking {tid} ---")
    res = pipeline.process(prompt, mode="Hỏi - Đáp", stream=False)
    err = res.get('error')
    df = res.get('data')
    if isinstance(df, pd.DataFrame):
        empty = df.empty
        shape = df.shape
    elif isinstance(df, dict):
        empty = all(v.empty for v in df.values() if isinstance(v, pd.DataFrame))
        shape = {k: getattr(v, 'shape', None) for k, v in df.items()}
    else:
        empty = True
        shape = None
    print(f"Error: {err} | Empty: {empty} | Shape: {shape}")
    print(f"SQL:\n{res.get('sql')}")
