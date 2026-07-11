import sys
sys.stdout.reconfigure(encoding='utf-8')
from src.query_control.agentic.agent_pipeline import AgenticPipeline
import pandas as pd

pipeline = AgenticPipeline()
q = "Tổng kiểm kê CSDL hộ nghèo Đắk Nông 2024 qua 3 bảng: Bảng 1: Thống kê theo huyện; Bảng 2: Thống kê theo quy mô nhân khẩu; Bảng 3: Thống kê theo nhóm dân tộc."
res = pipeline.process(q, mode="Hỏi - Đáp")
print("SQL:", res.get("sql"))
print("Has DF:", res.get("has_df"))
df = res.get("data")
if isinstance(df, pd.DataFrame):
    print("DF shape:", df.shape)
    print("DF head:\n", df.head())
elif isinstance(df, dict):
    print("Dict keys:", df.keys())
    for k, v in df.items():
        print(f"Key {k} shape:", v.shape if hasattr(v, 'shape') else len(v))
else:
    print("DF type:", type(df))
