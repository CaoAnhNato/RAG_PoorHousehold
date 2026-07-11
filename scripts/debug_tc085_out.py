import sys
sys.stdout.reconfigure(encoding='utf-8')
from src.query_control.agentic.agent_pipeline import AgenticPipeline

pipeline = AgenticPipeline()
q = "Báo cáo thực trạng đồng bào DTTS tại Đăk Glong 2024: Bảng 1: Thống kê hộ nghèo DTTS theo các xã; Bảng 2: Cơ cấu dân tộc (Mông, M'Nông, Dao...) của thành viên trong hộ nghèo."
out = pipeline.process(q, mode="Hỏi - Đáp", stream=False)
print("SQL:")
print(repr(out.get('sql')))
